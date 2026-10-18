from src.ingestion.loader import loader
from src.ingestion.chunker import chunking
from src.indexing.embedding import embedding
from src.indexing.vector_storage import indexing, save_index
from src.retrieval.retriever import reviewer
from src.retrieval.reranker import rerank
from src.generation.context_builder import build_context
from src.generation.genrater import generate_answer
from src.evaluator.corrective_reranking import corrective_reranking
from src.evaluator.evaluate_retrieval import evaluate_retrieval

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

        document = loader(self.filepath)

        an = chunking(document["document"])

        em = embedding(
            chunks=an["chunk"]
        )

        self.index = indexing(
            em["embedding"]
        )

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


    def evaluator(self, result):

        result1 = evaluate_retrieval(
            result,
            0.2
        )

        if result1 == "good":
            return result

        print("Initial retrieval was bad.")
        print("Starting corrective retrieval...")

        corrected_result = corrective_reranking(
            self.index_pt,
            self.chunks_pt,
            4
        )

        return corrected_result


    def genrater(self, promt):

        print("Index:", self.index_pt)
        print("Chunks:", self.chunks_pt)

        # Initial retrieval
        result = reviewer(
            promt,
            self.index_pt,
            self.chunks_pt,
            8
        )

        print("Initial retrieval:", result)

        # Initial reranking
        result = rerank(
            promt,
            result,
            top_k=5
        )

        print("Initial reranking:", result)

        # Evaluate retrieval
        status = evaluate_retrieval(
            result,
            0.3
        )

        # If retrieval is bad, try corrective retrieval
        if status == "bad":

            print("Chunks were not good.")
            print("Running corrective retrieval...")

            result = corrective_reranking(
                promt,
                self.index_pt,
                self.chunks_pt,
                4
            )

            # If corrective retrieval also fails
            if result == "bad":

                print("Corrective retrieval also failed.")

                return {
                    "answer": "I couldn't find enough relevant information in the uploaded document.",
                    "source": "document"
                }

            print("Corrective retrieval succeeded.")

        else:

            print("Initial retrieval was good.")

        # Build context only after retrieval is accepted
        context = build_context(result)

        print("We got context:")
        print(context)

        # Generate answer
        answer = generate_answer(
            promt,
            context
        )

        print("Generated answer:", answer)

        return {
            "answer": answer,
            "source": "document"
        }


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    global rag

    os.makedirs(
        "data/raw",
        exist_ok=True
    )

    filepath = f"data/raw/{file.filename}"

    with open(
        filepath,
        "wb"
    ) as buffer:

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

    return rag.genrater(
        promt.querry
    )