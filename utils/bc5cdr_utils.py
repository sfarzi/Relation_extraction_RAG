from bs4 import BeautifulSoup
from pathlib import Path
import json
import os
from tqdm import tqdm

# import minidom for prettify xml
from xml.dom import minidom

class Bc5cdrUtils:
    def __init__(self, split:str):
        splits = {
            "train": Path("datasets/1-BC5CDR/Prettified_CDR_TrainingSet.BioC.xml"),
            "test": Path("datasets/1-BC5CDR/prettified_CDR_TestSet.BioC.xml"),
            "dev": Path("datasets/1-BC5CDR/Prettified_CDR_DevelopmentSet.BioC.xml")
            }
        
        self.dataset_path = splits[split]
        with open(self.dataset_path, "r") as rx:
            self.xml_content = rx.read()

        self.soup = BeautifulSoup(self.xml_content, features="xml")



    def make_PER_DOCUMENT_MESH_TERM_dictionary(self):
        # Lists all document tags
        self.documents = self.soup.find_all('document')

        # add id of entities to map entities from entity id to entity name in relation tag
        MESH_TERM_dictionary = {}

        for document in self.documents:
            document_id = document.id.text
            passages = document.find_all('passage')
            for passage in passages:
                annotations = passage.find_all("annotation")
                for annotation in annotations:
                    try:
                        if annotation.find('infon', key='CompositeRole').text == 'CompositeMention':
                            continue
                    except:
                        pass
                    entity_name = annotation.find('text').text
                    entity_MESH = annotation.find('infon', key='MESH').text
                    for mesh in entity_MESH.split("|"):
                        MESH_TERM_dictionary.setdefault((mesh, document_id), set()).add(entity_name.lower())
        return MESH_TERM_dictionary
    

    
    def make_PER_DOCUMENT_TERM_MESH_dictionary(self):
        MESH_TERM_dictionary = self.make_PER_DOCUMENT_MESH_TERM_dictionary()
        TERM_MESH_dictionary = {}

        for (mesh, doc_id), names_list in MESH_TERM_dictionary.items():
            TERM_MESH_dictionary[(tuple(names_list), doc_id)] = mesh
        
        return TERM_MESH_dictionary


        


if __name__ == '__main__':
    util = Bc5cdrUtils('test')
    # a = util.make_PER_DOCUMENT_MESH_TERM_dictionary()
    u = util.make_PER_DOCUMENT_TERM_MESH_dictionary()
    print(u)