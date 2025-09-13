from tqdm import tqdm
from pathlib import Path
from src.umls.umls import UMLS
from utils.fileUtils import FilesUtils

class TermsInfo:
    def __init__(self, configs, split, umls_apikey):
        # configs
        self.configs = configs

        self.umls_apikey = umls_apikey

        self.split = split
        self.data = FilesUtils.read_json(self.configs['datasets']['bc5cdr'][self.split])

        # set path for saving inferences | Create path if necessary
        self.output_path = Path(self.configs['output']['terms_information']) / 'BC5CDR' / f'TermInformation_{self.split}.json'
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # create json file for terms information if not exists
        if not self.output_path.exists():
            FilesUtils.write_json(path=self.output_path, data={})
        

    def get(self):
        for record in tqdm(self.data):

            # read current info file
            self.terms_info_file_content = FilesUtils.read_json(path=self.output_path)

            # merge [title_entities_list] & [abstract_entities_list] into one list
            title_entities_list = record['title_entities']
            abstract_entities_list = record['abstract_entities']
            entities = title_entities_list + abstract_entities_list
            
            # FETCHING info from umls
            for entity in entities:
                if entity['IndividualMention']:
                    for individual_entity in entity['IndividualMention']:
                        # bc5cdr
                        bc5cdr_term_name = individual_entity['Individual_entity_name'].lower()
                        bc5cdr_term_type = individual_entity['Individual_entity_type']
                        bc5cdr_term_mesh_id = individual_entity['Individual_entity_MESH'][0]
                        bc5cdr_composite_term = entity["entity_name"].lower()

                        if bc5cdr_term_mesh_id in self.terms_info_file_content.keys():
                            continue
                        # umls
                        umls_info = UMLS(apikey=self.umls_apikey).term_info(mesh=bc5cdr_term_mesh_id, bc5cdr_term=bc5cdr_term_name)
                        MSH_source_term = umls_info['MSH_term'].lower()
                        cui = umls_info['cui']
                        definition = umls_info['definition']
                        definition_source = umls_info['definition_source']
                        termType = umls_info['termType']
                        synonyms = umls_info['synonyms']
                        relations = [[relation['entity_1_name'], relation['relation'], relation['entity_2_name']] for relation in umls_info['relations']]

                        one_entity_info = {
                            "bc5cdr_term_name": bc5cdr_term_name,
                            "bc5cdr_term_type": bc5cdr_term_type,
                            "MSH_source_term": MSH_source_term,
                            "cui": cui,
                            "definition": definition,
                            "definition_source": definition_source,
                            "termType": termType,
                            "synonyms": synonyms,
                            "relations": relations
                        }
                        self.terms_info_file_content[bc5cdr_term_mesh_id] = one_entity_info
                else:
                        # bc5cdr
                        bc5cdr_term_name = entity['entity_name'].lower()
                        bc5cdr_term_type = entity['entity_type']
                        bc5cdr_term_mesh_id = entity['entity_MESH'][0]
                        bc5cdr_composite_term = None

                        if bc5cdr_term_mesh_id in self.terms_info_file_content.keys():
                            continue

                        # umls
                        umls_info = UMLS(apikey=self.umls_apikey).term_info(mesh=bc5cdr_term_mesh_id, bc5cdr_term=bc5cdr_term_name)
                        MSH_source_term = umls_info['MSH_term'].lower()
                        cui = umls_info['cui']
                        definition = umls_info['definition']
                        definition_source = umls_info['definition_source']
                        termType = umls_info['termType']
                        synonyms = umls_info['synonyms']
                        relations = [[relation['entity_1_name'], relation['relation'], relation['entity_2_name']] for relation in umls_info['relations']]

                        one_entity_info = {
                            "bc5cdr_term_name": bc5cdr_term_name,
                            "bc5cdr_term_type": bc5cdr_term_type,
                            "bc5cdr_composite_term" : bc5cdr_composite_term,
                            "MSH_source_term": MSH_source_term,
                            "cui": cui,
                            "definition": definition,
                            "definition_source": definition_source,
                            "termType": termType,
                            "synonyms": synonyms,
                            "relations": relations
                        }
                        self.terms_info_file_content[bc5cdr_term_mesh_id] = one_entity_info
                
                # save per record 
                FilesUtils.write_json(path=self.output_path, data=self.terms_info_file_content)
            # break        




if __name__ == "__main__":
    # configs
    config_path = 'configs/configs.yaml'
    configs = FilesUtils.read_yaml(config_path)

    umls_apikey = '06d145b2-e6f7-4803-9bd0-5c2a9cfb3102'

    ti = TermsInfo(configs=configs, split='test', umls_apikey=umls_apikey)
    ti.get()
