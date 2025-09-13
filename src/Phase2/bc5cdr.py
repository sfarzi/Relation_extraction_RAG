import os
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from utils.fileUtils import FilesUtils
from src.models.llama import Llama
from src.models.medgemma import MedGemma
from src.models.openai import Chatgpt
from src.umls.umls import UMLS
from src.evaluation.calcuate_metrics import CalculateMetrics
from utils.bc5cdr_utils import Bc5cdrUtils
from utils.fileUtils import FilesUtils

class BC5CDR:
    def __init__(self, configs: dict, split:str, umls_apikey:str = None):
        
        self.split = split.lower()
        # configs
        self.configs = configs

        # set path for saving inferences
        self.output_path = Path(self.configs['output']['extracted_relations']) / 'BC5CDR'
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # prompt
        self.system_prompt = self.configs['prompts']['Phase2']['bc5cdr']['system']['v2-openai']

        # self.model_path = Path(self.configs['models']['model_path'])
        self.model_path = Path(self.configs['models']['model_path'])

        self.device_map = self.configs['models']['device_map']
        self.max_new_tokens = self.configs['models']['max_new_tokens']
        self.temperature = self.configs['models']['temperature']

        # init a model
        self.model =  Llama(
            model_path= self.model_path,
            device_map=self.device_map,
            system_prompt=self.system_prompt
            )

        # self.model =  MedGemma(
        #     model_path= self.model_path,
        #     device_map=self.device_map,
        #     system_prompt=self.system_prompt
        #     )

        # self.model = Chatgpt(
        #     model=self.configs["models"]["model_path"].split("/")[-1],
        #     instruction=self.system_prompt
        #     )
        
        # init UMLS class (this class will be used to map generated entities to MESH id.)
        if umls_apikey is None:
            self.umls_apikey = os.getenv('UMLS')
        else:
            self.umls_apikey = umls_apikey

        self.umls = UMLS(apikey=self.umls_apikey)

        # use CalculateMetrics class for metric calculations
        self.calc_metric = CalculateMetrics(configs=self.configs)

        # load TermInformation json file
        terms_info_file_path = Path(self.configs["output"]["terms_information"]) / f"BC5CDR/TermInformation_{self.split}.json"
        self.terms_info = FilesUtils.read_json(path=terms_info_file_path)
    
    
    def _dataloader(self):
        return FilesUtils.read_json(self.configs['datasets']['bc5cdr'][self.split])


    def extract_relations(self, ner_results):
        self.term_mesh_dictionary = Bc5cdrUtils(self.split).make_PER_DOCUMENT_TERM_MESH_dictionary()
        self.ner_results = ner_results

        # Load data from json
        self.data = self._dataloader()

        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # all results are being saved in output_dict list
        output_dict = {
            'phase': 2,
            'dataset': 'BC5CDR',
            'LLM': str(Path(*self.model_path.parts[-2:])),
            'method': 'UMLS',
            'split': self.split,
            'temperature': self.temperature,
            'system_prompt': self.system_prompt,
            'time': str(time),
            'results': []
        }
        
        print(f'[Phase 2] | Extracting relations from [BC5CDR|{self.split}] dataset')

        for record in tqdm(self.data):
            # STEP1: predict relations
            # loading title and abstract in variables
            document_id = record['id']
            title = record['title']
            abstract = record['abstract']

            extracted_meshes = self.ner_results["results"][document_id]["found_mesh"]
            additional_info_prompt = "Possible Entities and entity Types:\n"
            for mesh in extracted_meshes:
                term_name = self.terms_info[mesh]["MSH_source_term"]
                term_type = ", ".join(self.terms_info[mesh]["termType"])
                # term_definition = self.terms_info[mesh]["definition"]
                # term_synonyms = "\n".join(self.terms_info[mesh]["synonyms"])
                # one_term_additional_info = f"  -{term_name} -> {term_type}" + "\n"
                one_term_additional_info = f"  -{term_name}" + "\n"
                additional_info_prompt += one_term_additional_info


            # print(additional_info_prompt)

            ## inference (extracts relations)
            user_prompt = f"This is title: {title} and This is abstract: {abstract}\n\n{additional_info_prompt}"
            # user_prompt = f"Title: {title}\nAbstract: {abstract}\n\n{additional_info_prompt}"

            # print(f"prompt:\n {user_prompt}\n\n\n")
            pred_relations =  self.model.generate(
                user_prompt=user_prompt,
                max_new_tokens=self.max_new_tokens,
                temperature = self.temperature
            )
            # print(f"pred:\n{pred_relations}")
            # print(pred_relations)
            # "spontaneously hypertensive rats, clonidine\nspontaneously hypertensive rats, naloxone\nhypertension, alpha-methyldopa"
            pred_relations_list_mesh = []
            pred_relations_list_term = []
            for relation in pred_relations.split('\n'):
                entities = relation.split(', ')
                if len(entities)!=2:
                    continue
                pred_disease_name = entities[0].strip().lower()
                pred_chemical_name = entities[1].strip().lower()
                
                # for disease
                pred_disease_mesh = None
                for (names, doc_id), mesh in self.term_mesh_dictionary.items():
                    if document_id == doc_id and ((pred_disease_name in names) or (any(pred_disease_name in name for name in names))):
                        pred_disease_mesh = mesh
                        break
                if pred_disease_mesh is None:
                    try:
                        pred_disease_mesh = self.umls.find_mesh_source_descriptor_by_term(pred_disease_name)
                    except:
                        pass


                
                # for chemical
                pred_chemical_mesh = None
                for (names, doc_id), mesh in self.term_mesh_dictionary.items():
                    if document_id == doc_id and ((pred_chemical_name in names) or (any(pred_chemical_name in name for name in names))):
                        pred_chemical_mesh = mesh
                        break
                if pred_chemical_mesh is None:
                    try:
                        pred_chemical_mesh = self.umls.find_mesh_source_descriptor_by_term(pred_chemical_name)
                    except:
                        pass 

                pred_relations_list_mesh.append((pred_disease_mesh, pred_chemical_mesh))
                pred_relations_list_term.append((pred_disease_name, pred_chemical_name))






            
            # STEP2: add result of each record to output_dict
            # setting gold relations
            # gold_relations = ' | '.join([str((relation['disease'], relation['chemical'])) for relation in record['relations']])
            gold_relations_mesh = [(relation['disease_mesh'],relation['chemical_mesh']) for relation in record['relations']]
            gold_relations_term = [(relation['disease_name'],relation['chemical_name']) for relation in record['relations']]

            # saving one record
            one_record_temp = {
                'id': int(record['id']),
                'title': record['title'],
                'abstract': record['abstract'],
                'additional_info' : additional_info_prompt,
                'gold_relations_mesh': gold_relations_mesh,
                'pred_relations_mesh': pred_relations_list_mesh,
                'gold_relations_term': gold_relations_term,
                'pred_relations_term': pred_relations_list_term,
            }

            # add to output_dict and loop to the next reco
            output_dict['results'].append(one_record_temp)
            # break

        

        # STEP3: save output_dict in json
        # after iteration save output.dict in json file
        # model = str(self.model_path[-1])
        model_name = self.model_path.parts[-1]
        self.output_path = self.output_path / f'phase2_{self.split}_{model_name}_T_{time}.json'
        FilesUtils.write_json(path=self.output_path, data=output_dict)

        # Updates evaluation_results_file
        self.calc_metric.make_evaluation(extracted_relations_output=output_dict)






if __name__ == '__main__':
    # configs
    config_path = 'configs/configs.yaml'
    configs = FilesUtils.read_yaml(config_path)
    
    ner_results_path = "outputs/ner/ner_test_2025-09-11_17-07-39.json"
    ner_results = FilesUtils.read_json(path=ner_results_path)
    bc5cdr = BC5CDR(configs=configs, umls_apikey='06d145b2-e6f7-4803-9bd0-5c2a9cfb3102', split="test")
    bc5cdr.extract_relations(ner_results=ner_results)

    
