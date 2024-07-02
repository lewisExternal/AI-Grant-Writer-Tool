
from langchain_openai import OpenAIEmbeddings

try:
    import src.utils.config as config
except Exception as e:
    print(f'ERROR: {e}')
    import utils.config as config

embeddings = OpenAIEmbeddings(model=config.OPENAI_EMBEDDING_MODEL)

def get_open_ai_embeddings(text):
    if query_result := embeddings.embed_query(text):
        return query_result

def get_open_ai_embeddings_docs(docs):
    if query_result := embeddings.embed_documents(docs):
        return query_result



if __name__ =="__main__":
    pass 