import re
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from nltk.corpus import stopwords
from utils.fileUtils import FilesUtils
from src.Phase2.chroma import Chroma
from src.models.sapbert import sapBERT
from src.evaluation.evaluate_ner import EvaluateNer


class Ner:
    def __init__(self, configs, split, corpus_with_synonyms):
        self.configs = configs
        self.split = split.lower()
        self.corpus_with_synonyms = corpus_with_synonyms

        self.data_path = self.configs["datasets"]["bc5cdr"][split]
        self.data = FilesUtils.read_json(self.data_path)

        sapbert = sapBERT(model_path=self.configs['models']['embedder_model_path'])
        self.chroma = Chroma(configs=configs, embedder=sapbert, corpus_split='test', with_synonyms= corpus_with_synonyms)

        # stopwords
        english_stopwords = set(stopwords.words("english"))
        pubmed_stopwords = {
            'about','above','after','again','against','all','almost','alone','along','already','also',
            'although','always','among','an','and','any','are','aren’t','as','at','be','because','been',
            'before','being','below','between','both','but','by','can','cannot','could','did','do','does',
            'doing','done','during','each','either','enough','etc','for','from','further','had','has',
            'have','having','how','however','if','in','into','is','it','its','itself','just','may','might',
            'more','most','mostly','must','neither','never','no','nor','not','now','of','off','often','on',
            'only','or','other','our','out','over','own','per','perhaps','rather','same','seem','seen',
            'several','should','since','so','some','still','such','than','that','the','their','them',
            'then','there','therefore','these','they','this','those','through','thus','to','under','until',
            'up','upon','use','used','using','various','very','was','we','were','what','when','where',
            'whether','which','while','who','whose','why','will','with','within','without','would'
        }
        self.medical_stopwords = english_stopwords.union(pubmed_stopwords)

        # evaluation
        self.evaluator = EvaluateNer(configs=configs)
    


    def _remove_stopwords(self, text):
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [word for word in tokens if word not in self.medical_stopwords]
    
    


    def _term_extractor(self, text, threshold, stop_words, Combined_tokens, combine_length):
        self.threshold = threshold
        self.stop_words = stop_words
        self.Combined_tokens = Combined_tokens

        if self.stop_words:
            chunks = self._remove_stopwords(text=text)
        else:
            chunks = text.split(" ")
        
        if self.Combined_tokens:
            new_chunks = chunks
            for n in range(2,combine_length):
                combined_chunk = [' '.join(chars) for chars in zip(*(chunks[i:] for i in range(n)))]
                new_chunks += combined_chunk
            chunks = new_chunks
        
        # This is the output   
        extracted_terms = list()
        # used sets to avoid repetition
        extracted_terms_set = set()
        extracted_mesh_set = set()
        for chunk in chunks:
            retrieved = self.chroma._retrieve(query=chunk, top_k=1)
            distance = retrieved["distances"][0][0]
            mesh = retrieved["metadatas"][0][0]["mesh"]
            term = retrieved["documents"][0][0]
            if distance < self.threshold:
                if (term not in extracted_terms_set) and (mesh not in extracted_mesh_set):  
                    one_extracted_term = {
                        "term": term,
                        "mesh": mesh,
                        "distance": distance
                    }
                    extracted_terms.append(one_extracted_term)
                    extracted_terms_set.add(term)
                    extracted_mesh_set.add(mesh)
        return extracted_terms




    def main(self, threshold, stop_words, Combined_tokens, combine_length):
        time = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        ner_output = {
            "time": time,
            "config": f"threshold={threshold} | stop_words={stop_words} | Combined_tokens={Combined_tokens} | combine_length={combine_length} | corpus_with_synonyms: {self.corpus_with_synonyms}",
            "results": {}
        }
        print(ner_output["config"])
        desc = f"Extracting terms from {self.split} split."
        for record in tqdm(self.data, desc=desc, unit='record'):
            id = record["id"]
            text = record["title"] + " " + record["abstract"]
            # gold
            gold_mesh = set()
            gold_terms = set()
            bc5cdr_terms = record["title_entities"] + record["abstract_entities"]
            for bc5cdr_term in bc5cdr_terms:
                gold_terms.add(bc5cdr_term["entity_name"].lower())
                for mesh in bc5cdr_term["entity_MESH"]:
                    gold_mesh.add(mesh)
            
            # prediction
            retrieved_terms = self._term_extractor(
                text=text, threshold=threshold, 
                stop_words=stop_words, 
                Combined_tokens=Combined_tokens,
                combine_length=combine_length
                )
            found_terms = set()
            found_mesh = set()
            for retrieved_term in retrieved_terms:
                found_terms.add(retrieved_term["term"])
                found_mesh.add(retrieved_term["mesh"])
    
            result_for_one_record = {
                "gold_terms": list(gold_terms),
                "gold_mesh": list(gold_mesh),
                "found_terms": list(found_terms),
                "found_mesh": list(found_mesh)
            }
            ner_output["results"][id] = result_for_one_record
        
        # save
        self.ner_output_save_path = Path(self.configs["output"]["ner"] ) / f"ner_{self.split}_{time}.json"
        self.ner_output_save_path.parent.mkdir(exist_ok=True, parents=True)
        FilesUtils.write_json(data=ner_output, path=self.ner_output_save_path)

        # evaluate
        r = self.evaluator.eval(ner_results_path=self.ner_output_save_path)
        print(r)

if __name__ == "__main__":
    configs = FilesUtils.read_yaml(path="configs/configs.yaml")
    
    # args
    split = configs["ner"]["split"]
    corpus_with_synonyms = configs["ner"]["corpus_with_synonyms"]
    threshold = configs["ner"]["threshold"]
    stop_words = configs["ner"]["stop_words"]
    Combined_tokens = configs["ner"]["Combined_tokens"]

    ner = Ner(configs=configs, split=split, corpus_with_synonyms=corpus_with_synonyms)
    ner.main(threshold=threshold, stop_words=stop_words, Combined_tokens=Combined_tokens, combine_length=5)
