from langchain_community.embeddings import HuggingFaceEmbeddings

_EMBEDDINGS = None

def get_embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={"device": "cpu"},   # GPU 있으면 "cuda"
            encode_kwargs={"normalize_embeddings": True}
        )
    return _EMBEDDINGS
