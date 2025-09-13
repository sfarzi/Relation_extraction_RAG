from rank_bm25 import BM25Okapi
from utils.fileUtils import FilesUtils

class LexicalSearch:
    def __init__(self, corpus_split):
        self.corpus_split = corpus_split.lower()

    def _make_corpus(self):
        corpus = list()
        terms_dictionary = FilesUtils.read_json(f"outputs/Term_Id_dictionary/BC5CDR/{self.corpus_split}.json")
        for term, _ in terms_dictionary.items():
            corpus.append(term)
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        return bm25, corpus
    
    def _tokenize(self, text): 
        return text.lower().split()

    def search(self, query, topk):
        bm25, corpus = self._make_corpus()
        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        top_docs = bm25.get_top_n(tokenized_query, corpus, n=5)
        print(top_docs)






if __name__ == "__main__":
    ls = LexicalSearch(corpus_split="test")
    query = "\"Real-world\" data on the efficacy and safety of lenalidomide and dexamethasone in patients with relapsed/refractory multiple myeloma who were treated according to the standard clinical practice: a study of the Greek Myeloma Study Group."
    ls.search(query=query, topk=5)


# query = "Valproic acid (VPA) was given to 24 epileptic patients who were already being treated with other antiepileptic drugs. A standardized loading dose of VPA was administered, and venous blood was sampled at 0, 1, 2, 3, and 4 hours. Ammonia (NH3) was higher in patients who, during continuous therapy, complained of drowsiness (7 patients) than in those who were symptom-free (17 patients), although VPA plasma levels were similar in both groups. By measuring VPA-induced changes of blood NH3 content, it may be possible to identify patients at higher risk of obtundation when VPA is given chronically."
# tokenized_query = tokenize(query)

# # scores per document
# scores = bm25.get_scores(tokenized_query)   # list of floats aligned with corpus order
# # top-N documents
# top_docs = bm25.get_top_n(tokenized_query, corpus, n=1)

# print("Scores:", scores)
# print("Top docs:")
# for d in top_docs:
#     print("-", d)
