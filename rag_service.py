from functools import lru_cache

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


load_dotenv()


@lru_cache(maxsize=1)
def get_query_engine():
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.llm = OpenAI(model="gpt-4o-mini")

    documents = SimpleDirectoryReader("data").load_data()
    parser = TokenTextSplitter(chunk_size=256, chunk_overlap=20)
    nodes = parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes)
    return index.as_query_engine(similarity_top_k=2)


def answer_with_rag(message: str) -> dict:
    response = get_query_engine().query(message)
    sources = [
        {
            "file_name": node.metadata.get("file_name"),
            "file_path": node.metadata.get("file_path"),
            "text": node.text,
        }
        for node in response.source_nodes
    ]
    return {"answer": str(response), "sources": sources}


def clear_query_engine_cache() -> None:
    get_query_engine.cache_clear()
