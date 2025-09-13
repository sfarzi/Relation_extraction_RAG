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
    def __init__(self, configs: dict, umls_apikey:str = None):
        # configs
        self.configs = configs

        # set path for saving inferences
        self.output_path = Path(self.configs['output']['extracted_relations']) / 'BC5CDR'
        # Create path if necessary
        self.output_path.mkdir(parents=True, exist_ok=True)
        

        # set model
        self.system_prompt = self.configs['prompts']['Phase1']['bc5cdr']['system']['v-openai']

        # self.model_path = Path(self.configs['models']['model_path'])
        self.model_path = Path(self.configs['models']['model_path'])

        self.device_map = self.configs['models']['device_map']
        self.max_new_tokens = self.configs['models']['max_new_tokens']
        self.temperature = self.configs['models']['temperature']

        # # init a model
        # self.model =  Llama(
        #     model_path= self.model_path,
        #     device_map=self.device_map,
        #     system_prompt=self.system_prompt
        #     )

        # self.model =  MedGemma(
        #     model_path= self.model_path,
        #     device_map=self.device_map,
        #     system_prompt=self.system_prompt
        #     )

        self.model = Chatgpt(
            model=self.configs["models"]["model_path"].split("/")[-1],
            instruction=self.system_prompt
            )
        
        # init UMLS class (this class will be used to map generated entities to MESH if.)
        if umls_apikey is None:
            self.umls_apikey = os.getenv('UMLS')
        else:
            self.umls_apikey = umls_apikey

        self.umls = UMLS(apikey=self.umls_apikey)

        # use CalculateMetrics class for metric calculations
        self.calc_metric = CalculateMetrics(configs=self.configs)
    
    
    def _dataloader(self, split):
        self.split = split
        return FilesUtils.read_json(self.configs['datasets']['bc5cdr'][self.split])

    

    def extract_relations(self, split):
        self.term_mesh_dictionary = Bc5cdrUtils(split).make_PER_DOCUMENT_TERM_MESH_dictionary()

        # Load data from json
        self.data = self._dataloader(split=split)

        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # all results are being saved in output_dict list
        output_dict = {
            'phase': 1,
            'dataset': 'BC5CDR',
            'LLM': str(Path(*self.model_path.parts[-2:])),
            'method': 'PromptEngineering',
            'split': self.split,
            'temperature': self.temperature,
            'system_prompt': self.system_prompt,
            'time': str(time),
            'results': []
        }
        
        print(f'Extracting relations from [BC5CDR|{self.split}] dataset')

        for record in tqdm(self.data):
            # STEP1: predict relations
            # loading title and abstract in variables
            document_id = record['id']
            title = record['title']
            abstract = record['abstract']

            ## inference (extracts relations)
            # user_prompt = f"This is title: {title} and This is abstract: {abstract}"
            user_prompt = f"Title: {title}\nAbstract: {abstract}"
            pred_relations =  self.model.generate(
                user_prompt=user_prompt,
                max_new_tokens=self.max_new_tokens,
                temperature= self.temperature
            )
            # backup = {}
            # FilesUtils.append_text(path="G:\\Thesis\\backup.txt", data=f"______\ndoc_id={document_id}\n\n{pred_relations}\n______\n\n")
            

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
                'gold_relations_mesh': gold_relations_mesh,
                'pred_relations_mesh': pred_relations_list_mesh,
                'gold_relations_term': gold_relations_term,
                'pred_relations_term': pred_relations_list_term,
            }

            # add to output_dict and loop to the next reco
            output_dict['results'].append(one_record_temp)
            

        

        # STEP3: save output_dict in json
        # after iteration save output.dict in json file
        # model = str(self.model_path[-1])
        model_name = self.model_path.parts[-1]
        self.output_path = self.output_path / f'phase1_{split}_{model_name}_T_{time}.json'
        FilesUtils.write_json(path=self.output_path, data=output_dict)

        # Updates evaluation_results_file
        self.calc_metric.make_evaluation(extracted_relations_output=output_dict)






if __name__ == '__main__':
    # configs
    config_path = 'configs/configs.yaml'
    configs = FilesUtils.read_yaml(config_path)
  
    bc5cdr = BC5CDR(configs=configs, umls_apikey='06d145b2-e6f7-4803-9bd0-5c2a9cfb3102')
    bc5cdr.extract_relations(split='test')

    
