from tqdm import tqdm
from utils.fileUtils import FilesUtils
from pathlib import Path

class MakeTermIdDictionary:
    def __init__(self, configs, split):
        self.split = split.lower()
        self.configs = configs
        terms_info_path = Path(self.configs['output']['terms_information']) / f'BC5CDR/TermInformation_{self.split}.json'
        self.terms_info = FilesUtils.read_json(terms_info_path)

    def run(self, with_synonyms=True):
        self.dictionary = dict()
        for mesh, info in tqdm(self.terms_info.items()):
            set_of_terms_per_mesh = set()
            set_of_terms_per_mesh.add(info['MSH_source_term'].lower())
            if with_synonyms:
                for synonym in info['synonyms']:
                    set_of_terms_per_mesh.add(synonym.lower())
            for term in set_of_terms_per_mesh:
                self.dictionary[term] = mesh
        
        # save
        detail = "with_synonyms" if with_synonyms else "without_synonyms"
        output_path = Path(self.configs["output"]["term_id_dictionary"]) / "BC5CDR" / f"term_id_dictionary_{self.split}_{detail}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        FilesUtils.write_json(path=output_path, data=self.dictionary)
        print(f"File saved at [{output_path}]")
        
        return self.dictionary



if __name__ == "__main__":
    configs = FilesUtils.read_yaml(path="configs/configs.yaml")
    dic = MakeTermIdDictionary(configs=configs, split="test")
    dic.run(with_synonyms=False)