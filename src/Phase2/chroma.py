import re
import nltk
import chromadb
from tqdm import tqdm
from pathlib import Path
from utils.fileUtils import FilesUtils
from src.Phase2.make_term_id_dictionary import MakeTermIdDictionary

# nltk.download('stopwords')

class Chroma:
    def __init__(self, configs, embedder, corpus_split, with_synonyms):
        self.configs = configs
        self.corpus_split = corpus_split.lower()
        self.with_synonyms = with_synonyms

        # embedder
        self.corpus_split = corpus_split.lower()
        self.embedder = embedder

        # Loading term_id dictionary
        print("[Chroma] | Making Dictionary...")
        dict_maker = MakeTermIdDictionary(configs=self.configs, split=self.corpus_split)
        self.term_id_dictionary = dict_maker.run(with_synonyms=self.with_synonyms)
        self.terms = [term for term, _ in self.term_id_dictionary.items()]
        self.metadata = [{"mesh":id} for _,id in self.term_id_dictionary.items()]
        self.ids = [f"id{i}" for i in range(len(self.terms))]

        # ChromaDB
        detail = "with_synonyms" if with_synonyms else "without_synonyms"
        self.collection_name = f"{self.corpus_split}_{detail}" 

        # Chroma database config
        self.db_save_path = self.configs['chroma']['db_save_path']

        # Creates or load a Chroma database
        self.client = chromadb.PersistentClient(path=self.db_save_path)
        self._get_collection()
        self._add_terms_to_chroma()

    def _get_collection(self):
        """
        This part handels collection. If DB has the collection then loads it, else, creates a collection.
        """
        # Chroma collection config
        self.similarity_metric = self.configs['chroma']['similarity_metric']
        self.ef_search = self.configs['chroma']['ef_search']
        self.collection_configuration = {"hnsw": {"space": self.similarity_metric, "ef_search": self.ef_search}}

        # Gets ALL chroma collections exsiting in chroma database
        self.exisiting_collections = [coll.name for coll in self.client.list_collections()]

        # If exists, loads the collection, Else, creates a collection.
        self.need_to_create_collection = True
        self.need_to_embed = True
        
        if self.collection_name in self.exisiting_collections:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"[Chroma] | {self.collection_name} collection loaded.")
            self.need_to_create_collection = False
            if self.collection.count() == len(self.terms):
                self.need_to_embed = False

        if self.need_to_create_collection:
            print(f"[Chroma] | {self.collection_name} collection created.")
            self.collection = self.client.create_collection(
                name = self.collection_name,
                configuration = self.collection_configuration
            )

    def _embed_terms(self):
        """
        Embeds documents. This method is used in [add_dataset_to_chroma] method.
        """
        # embed
        print(f"[Chroma] | Embedding [{len(self.terms)}] terms ...")
        self.terms_embeddings = self.embedder.embed(text=self.terms)
        return self.terms_embeddings
        
    def _add_terms_to_chroma(self):
        """
        Add terms to the chromaDB. It uses _embed_dataset() method.
        """

        # if collection is loaded, We dont need embedding and adding to chroma
        if not self.need_to_embed:
            return

        # calls embedding method
        self.embedded_terms = self._embed_terms()
        self.terms_length = len(self.embedded_terms)
        
        add_batch_size = 4000
        try:
            tqdm_desc = f"[Chroma] | Adding [{self.terms_length}] embedding terms to chromaDB..."
            for i in tqdm(range(0, self.terms_length, add_batch_size), desc=tqdm_desc):
                self.collection.add(
                    ids = self.ids[i:i+add_batch_size],
                    documents = self.terms[i:i+add_batch_size],
                    metadatas= self.metadata[i:i+add_batch_size],
                    embeddings = self.embedded_terms[i:i+add_batch_size],
                )
        except Exception as e:
            print(e)

    def _retrieve(self, query:str, top_k:int):

        self.query = query
        self.query_embeddings = self.embedder.embed(text = self.query)

        self.query_results = self.collection.query(
            query_embeddings=self.query_embeddings,
            n_results=top_k
            )
        return self.query_results