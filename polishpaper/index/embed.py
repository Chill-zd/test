from __future__ import annotations
import numpy as np

class Embedder:
    def __init__(self,model_name:str="BAAI/bge-small-en-v1.5",device:str="cpu",model=None):
        self.fingerprint=model_name+":"+device
        self.model=model
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model=SentenceTransformer(model_name,device=device)
    def encode(self,texts:list[str]):
        a=np.asarray(self.model.encode(texts,normalize_embeddings=True),dtype=np.float32)
        return a.reshape((len(texts),-1))
