import warnings
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*Possible set union at position.*"
)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spacy
from utils.fileUtils import FilesUtils
from src.Phase3.models.llama import Llama
from src.Phase3.models.medgemma import MedGemma
from src.Phase3.models.openai import Chatgpt
from src.Phase3.models.sapbert import sapBERT

class HyDE:
    def __init__(self, configs, generator, embedder):
        self.configs = configs
        self.model = generator
        self.embedder = embedder

        self.nlp = spacy.load("en_core_sci_sm")
        self.nlp.add_pipe("sentencizer")

    def _make_hypothetical_document(self, disease, chemical):
        disease = disease.lower()
        chemical = chemical.lower()
        hyde_system_prompt = self.configs["prompts"]["Phase3"]["make_hypothetical_document_system_prompt"]
        hyde_user_prompt = self.configs["prompts"]["Phase3"]["make_hypothetical_document_user_prompt"].format(chemical=chemical, disease=disease)
        
        hypothetical_document = self.model.generate(
            user_prompt=hyde_user_prompt,
            system_prompt=hyde_system_prompt,
            max_new_tokens=100,
            temperature=0.8
            )
        # print(hypothetical_document)
        return hypothetical_document
    
    def _chunk_text(self, text: str, max_tokens=20, overlap=0):
        text = text.lower()
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        chunks = []
        current_chunk = []
        current_len = 0
        for sent in sentences:
            sent_len = len(sent.split())
            if current_len + sent_len > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                overlap_tokens = current_chunk[-overlap:] if overlap > 0 else []
                current_chunk = overlap_tokens + sent.split()
                current_len = len(current_chunk)
            else:
                current_chunk.extend(sent.split())
                current_len += sent_len
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    

    def _find_similar_sentence(self, text, disease, chemical, topk=2):
        disease = disease.lower()
        chemical = chemical.lower()

        hypothetical_document = self._make_hypothetical_document(disease, chemical)
        hypothetical_document_emb = self.embedder.embed(hypothetical_document)

        # print(f"\nhypothetical_document:\n{hypothetical_document}")

        main_text = text
        main_text_chunks = self._chunk_text(main_text)
        main_text_chunks_emb = self.embedder.embed(main_text_chunks)
        
        sims = cosine_similarity(hypothetical_document_emb ,main_text_chunks_emb)[0]
        top_2 = np.argsort(sims)[-topk:][::-1]
       

        similar_sentence1 = main_text_chunks[top_2[0]]
        similar_sentence2 = main_text_chunks[top_2[1]]

        similar_sentences = [similar_sentence1, similar_sentence2]
        return similar_sentences

    def _judge(self, chemical, disease, similar_sentences):
        judge_system_prompt = self.configs["prompts"]["Phase3"]["judge_system_prompt"]
        judge_user_prompt = self.configs["prompts"]["Phase3"]["judge_user_prompt"].format(chemical=chemical, disease=disease, snippet1=similar_sentences[0], snippet2=similar_sentences[1])

        
        is_relation = self.model.generate(
            user_prompt=judge_user_prompt,
            system_prompt=judge_system_prompt,
            max_new_tokens=20,
            temperature=0.1
            )
        return is_relation.strip()
    
    def main(self, text, chemical, disease):
        similar_sentences = self._find_similar_sentence(
            text = text,
            chemical = chemical, 
            disease =disease
            )

        return self._judge(chemical=chemical, disease=disease, similar_sentences=similar_sentences)



if __name__ == "__main__":
    from pathlib import Path
    configs = FilesUtils.read_yaml(path="configs/configs.yaml")
    model_path = Path(configs["models"]["model_path"])
    device_map = configs["models"]["device_map"]
    # model =  Llama(
    #             model_path= model_path,
    #             device_map=device_map
    #             )
    model = Chatgpt(
        model=configs["models"]["model_path"].split("/")[-1]
        )
    embedder_model_path = configs["models"]["embedder_model_path"]
    embedder = sapBERT(model_path=embedder_model_path)

    text = "Famotidine is a histamine H2-receptor antagonist used in inpatient settings for prevention of stress ulcers and is showing increasing popularity because of its low cost. Although all of the currently available H2-receptor antagonists have shown the propensity to cause delirium, only two previously reported cases have been associated with famotidine. The authors report on six cases of famotidine-associated delirium in hospitalized patients who cleared completely upon removal of famotidine. The pharmacokinetics of famotidine are reviewed, with no change in its metabolism in the elderly population seen. The implications of using famotidine in elderly persons are discussed."
    chemical = "delirium"
    disease = "Famotidine"

    hyde = HyDE(configs=configs,generator=model, embedder=embedder)
    similar_sentences = hyde._find_similar_sentence(
        text = text,
        chemical = chemical, 
        disease =disease
    )

    print(similar_sentences)

    is_relation = hyde._judge(chemical=chemical, disease=disease, similar_sentences=similar_sentences)
    print(is_relation)