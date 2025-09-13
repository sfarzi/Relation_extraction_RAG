import numpy as np
import torch
from tqdm.auto import tqdm
from transformers import AutoTokenizer, AutoModel  


class sapBERT:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)  
        self.model = AutoModel.from_pretrained(model_path).cuda()

    def embed(self, text):
        if isinstance(text, str):
            text = [text]

        bs = 128 
        all_embs = []
        for i in np.arange(0, len(text), bs):
            toks = self.tokenizer.batch_encode_plus(text[i:i+bs], 
                                            padding="max_length", 
                                            max_length=25, 
                                            truncation=True,
                                            return_tensors="pt")
            toks_cuda = {}
            for k,v in toks.items():
                toks_cuda[k] = v.cuda()
            cls_rep = self.model(**toks_cuda)[0][:,0,:] 
            all_embs.append(cls_rep.cpu().detach().numpy())

        all_embs = np.concatenate(all_embs, axis=0)
        return all_embs


if __name__ == "__main__":
    embdr = sapBERT(model_path="models/cambridgeltl/SapBERT-from-PubMedBERT-fulltext")
    a = embdr.embed(["lithium", "lithium carbonate"])
    print(a)