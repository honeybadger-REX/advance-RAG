from src.ingestion.loader import loader
from src.ingestion.chunker import chunking
from src.indexing.embedding import embedding
from src.indexing.vector_storage import indexing, save_index
from src.retrieval.retriever import reviewer
from src.retrieval.reranker import rerank
from src.generation.context_builder import build_context
from src.generation.genrater import generate_answer
from src.evaluator.corrective_reranking import corrective_reranking
from src.evaluator. evaluate_retrieval import  evaluate_retrieval



from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File

import os
import shutil


app = FastAPI()

rag = None


class RAG_pipleline:

    def __init__(self, filepath, filename):

        self.filepath = filepath
        self.filename = filename

        self.name = self.filename.rsplit(".", 1)[0]

        self.index_pt = f"vector_store/{self.name}_index.faiss"
        self.chunks_pt = f"vector_store/{self.name}_chunks.json"

        self.index = None

    def pdf_CEIIS(self):

        # Loading
        document = loader(self.filepath)

        # Chunking
        an = chunking(document["document"])

        # Embedding
        em = embedding(
            chunks=an["chunk"]
        )

        # FAISS indexing
        self.index = indexing(
            em["embedding"]
        )

        # Save index + chunks
        save_index(
    self.index,
    an["chunk"],
    self.index_pt,
    self.chunks_pt
)

        print("PDF processing completed.")

        return {
            "message": "PDF processed successfully",
            "document": self.name
        }

    def evaluator(self,result):
        result1 = evaluate_retrieval(result,0.3)
        if result1 is None:
            print("result was not thier")
            return "break"
        if result1 == "good":
            return result
        else:
            return corrective_reranking(result, self.index_pt,self.chunks_pt,4)




    def genrater(self, promt):

        print("Index:", self.index_pt)
        print("Chunks:", self.chunks_pt)

        # Retrieval
        result = reviewer(
            promt,
            self.index_pt,
            self.chunks_pt,
            8
        )
        result = rerank(promt, result, top_k=5)
        result = self.evaluator(result)
        if result == "bad":
            print("chunk were go bad to  answer")
            break 
            return "I couldn't find enough relevant information in the uploaded document."
        else:
            print("we got result:", result)

        # Context construction
        context = build_context(result)

        print("we got context:", context)

        # Generation
        answer = generate_answer(
            promt,
            context
        )

        print("Generated answer:", answer)

        return answer


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global rag

    os.makedirs(
        "data/raw",
        exist_ok=True
    )

    filepath = f"data/raw/{file.filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    rag = RAG_pipleline(
        filepath,
        file.filename
    )

    result = rag.pdf_CEIIS()

    return result


class querry(BaseModel):
    querry: str


@app.post("/Home")
def answer(promt: querry):

    if rag is None:
        return {
            "error": "Please upload a PDF first."
        }

    print(promt)

    return {
        "answer": rag.genrater(
            promt.querry
        )
    }


