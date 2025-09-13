import yaml
import json


class FilesUtils:
    @staticmethod
    def read_yaml(path):
        with open(path, 'r', encoding='utf-8') as ry:
            return yaml.safe_load(ry)
        
    @staticmethod
    def read_json(path):
        with open(path, 'r', encoding='utf-8') as rj:
            return json.load(rj)
        
    @staticmethod
    def write_json(path, data):
        with open(path, 'w', encoding='utf-8') as wj:
            json.dump(data, wj, indent=4, ensure_ascii=False)