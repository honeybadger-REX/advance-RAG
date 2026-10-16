from langchain_openai import ChatOpenAI


# Load LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def generate_answer(query, context):
    """
    Generate an answer using the retrieved context.
    """

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context,
say that you don't have enough information.

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content