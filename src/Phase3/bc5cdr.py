from datetime import datetime
from tqdm import tqdm
from utils.fileUtils import FilesUtils
from pathlib import Path
from src.Phase3.models.llama import Llama
from src.Phase3.models.medgemma import MedGemma
from src.Phase3.models.openai import Chatgpt
from src.Phase3.models.sapbert import sapBERT
from src.Phase3.HyDE import HyDE
from src.evaluation.calcuate_metrics import CalculateMetrics


class BC5CDR:
    def __init__(self, configs, split):
        self.configs = configs
        self.split = split.lower()

        dataset_path = self.configs["datasets"]["bc5cdr"][self.split]
        self.data = FilesUtils.read_json(path=dataset_path)

        terms_info_path = Path(self.configs["output"]["terms_information"]) / f"BC5CDR/TermInformation_{self.split}.json"
        self.terms_info = FilesUtils.read_json(path=terms_info_path)

        self.ner_results = FilesUtils.read_json(path="outputs/ner/ner_test_2025-09-11_17-07-39.json")

        self.model_path = Path(self.configs["models"]["model_path"])
        self.device_map = self.configs["models"]["device_map"]
        

        # init a model
        if self.model_path == Path("models/meta-llama/Llama-3.2-3B-Instruct"):
            self.model =  Llama(
                model_path= self.model_path,
                device_map=self.device_map
                )

        if self.model_path == Path("models/google/medgemma-4b-it"):
            self.model =  MedGemma(
                model_path= self.model_path,
                device_map=self.device_map
                )

        if self.model_path == Path("openai/gpt-4.1-2025-04-14"):
            self.model = Chatgpt(
                model=self.configs["models"]["model_path"].split("/")[-1]
                )

        embedder_model_path = self.configs["models"]["embedder_model_path"]
        self.embedder = sapBERT(model_path=embedder_model_path)


        self.hyde = HyDE(configs=self.configs, generator=self.model, embedder=self.embedder)

        self.time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dict = {
            'phase': 3,
            'dataset': 'BC5CDR',
            'LLM': str(Path(*self.model_path.parts[-2:])),
            'method': 'HyDE',
            'split': self.split,
            'temperature': 0.0,
            'system_prompt': "",
            'time': str(self.time),
            'results': []
        }

        self.output_path = Path(self.configs['output']['extracted_relations']) / 'BC5CDR'
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.calc_metric = CalculateMetrics(configs=self.configs)






    def main(self):
        desc = "Extractin Relations"
        for record in tqdm(self.data, desc=desc):
            doc_id = record["id"]
            title = record["title"]
            abstract = record["abstract"]

            text = title + " " + abstract

            found_mesh = self.ner_results["results"][doc_id]["found_mesh"]

            # separating found entities
            chemicals = []
            diseases = []
            for mesh in found_mesh:
                try:
                    mesh_type = self.terms_info[mesh]["bc5cdr_term_type"]
                    entitiy = {
                        "mesh": mesh,
                        "name": self.terms_info[mesh]["MSH_source_term"]
                        }
                    if mesh_type == "Chemical":
                        chemicals.append(entitiy)
                    else:
                        diseases.append(entitiy)
                except:
                    continue
            
            # making pairs
            cid_pairs = []
            for disease in diseases:
                for chemical in chemicals:
                    one_cid_pair = {
                        "disease_name": disease["name"],
                        "disease_mesh": disease["mesh"],
                        "chemical_name": chemical["name"],
                        "chemical_mesh": chemical["mesh"],
                        "is_relation": False
                    }
                    cid_pairs.append(one_cid_pair)
            
            pred_relations_list_mesh = []
            pred_relations_list_term = []
            for cid_pair in cid_pairs:
                chemical_name = cid_pair["chemical_name"]
                chemical_mesh = cid_pair["chemical_mesh"]
                disease_name = cid_pair["disease_name"]
                disease_mesh = cid_pair["disease_mesh"]

                is_relation = self.hyde.main(text=text, chemical=chemical_name, disease=disease_name).lower()
                if is_relation == 'true':
                    cid_pair["is_relation"] = True
                    pred_relations_list_mesh.append((disease_mesh, chemical_mesh))
                    pred_relations_list_term.append((disease_name, chemical_name))
                    continue

            gold_relations_mesh = [(relation['disease_mesh'],relation['chemical_mesh']) for relation in record['relations']]
            gold_relations_term = [(relation['disease_name'],relation['chemical_name']) for relation in record['relations']]


            one_record_temp = {
                'id': int(record['id']),
                'title': record['title'],
                'abstract': record['abstract'],
                'gold_relations_mesh': gold_relations_mesh,
                'pred_relations_mesh': pred_relations_list_mesh,
                'gold_relations_term': gold_relations_term,
                'pred_relations_term': pred_relations_list_term,
            }
            self.output_dict['results'].append(one_record_temp)
            # break


        # save extractions
        model_name = self.model_path.parts[-1]
        self.output_path = self.output_path / f'phase3_{self.split}_{model_name}_T_{self.time}.json'
        FilesUtils.write_json(path=self.output_path, data=self.output_dict)

        # Updates evaluation_results_file
        self.calc_metric.make_evaluation(extracted_relations_output=self.output_dict)





if __name__ == "__main__":
    # configs
    config_path = 'configs/configs.yaml'
    configs = FilesUtils.read_yaml(config_path)

    bc5cdr = BC5CDR(configs=configs, split="test")
    bc5cdr.main()
