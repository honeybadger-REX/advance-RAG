from src.ingestion.loader import loader 
from src.ingestion.chunker import chunking
from src.indexing.embedding import embedding
from src.indexing.vector_storage import  indexing ,save_index
from src.retrieval.retriever import reviewer
from src.generation.context_builder import build_context
from src.generation.genrater import generate_answer
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi import FastAPI ,UploadFile, File
import os
import shutil


app = FastAPI()





class RAG_pipleline:
    def __init__(self,filepath,filename):
        self.filepath = filepath
        self.filename = filename
        self.name = self.filename.rsplit(".", 1)[0]
        self.index_pt = f"vector_store/{self.name}_index.faiss"
        self.chunks_pt = f"vector_store/{self.name}_chunks.json"
        self.index = None

    def pdf_CEIIS(self):
          document = loader(self.filepath)
        
            # Chunking
          an = chunking(document["document"])
        
            # Embedding
          em = embedding(chunks=an["chunk"])
        
            # FAISS indexing
          self.index = indexing(em["embedding"])
   
          print(self.name)
            # Save index + chunks
          save_index(self.index,an["chunk"],self.name)

    def genrater(self,promt):
        print(self.index_pt)

        print(self.chunks_pt)
        result = reviewer(promt,self.index_pt,self.chunks_pt,3)
        print("we got result"+"  "+ result)
        context = build_context(result)
        print("we got context"+ " "+ context)
        print(generate_answer(promt,context))
        print("compeleted the genrationg")

rag = None

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    os.makedirs("data/raw", exist_ok=True)

    filepath = f"data/raw/{file.filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    rag = RAG_pipleline(filepath,file.filename)
    result = rag.pdf_CEIIS()

    return result


class querry(BaseModel):
    querry: str


@app.post("/Home/")
def answer(promt: querry):
    print(promt)
    if rag is None:
        return {"error": "Please upload a PDF first."}

    return {"answer": rag.genrater(promt.querry)}






