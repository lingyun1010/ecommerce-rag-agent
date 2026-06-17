import os
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()

print("Starting...")

# ✅ 明确 embedding + LLM（关键）
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")

documents = SimpleDirectoryReader("data").load_data()

print(f"Loaded {len(documents)} documents")

parser = SentenceSplitter(chunk_size=256, chunk_overlap=20)

nodes = parser.get_nodes_from_documents(documents)

index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine(similarity_top_k=2)

queries = [
    "Which shampoo is suitable for oily scalp?",
    "What shampoo is best for greasy hair?",
    "Recommend shampoo for oil control"
]

while True:
    question = input("Question: ")

    if question == "exit":
        break

    response = query_engine.query(question)

    print(response)

    print("Source nodes:")
    for node in response.source_nodes:
        print("---")
        print(node.text)
        print(node.metadata)

# for query in queries:
#     response = query_engine.query(query)

#     print(f"Query: {query}")
#     print(f"Response: {response}")

#     print("Source nodes:")
#     for node in response.source_nodes:
#         print("---")
#         print(node.text)
#         print(node.metadata)