import os 
import PyPDF2
from math import ceil
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings



try:
    import src.utils.langchain_utils as langchain_utils
    import src.utils.pgvector_utils as pgvector_utils
    import src.utils.config as config
except Exception as e:
    print(f'ERROR importing: {e}')
    # for running in a virtual env  
    import utils.langchain_utils as langchain_utils
    import utils.pgvector_utils as pgvector_utils
    import utils.config as config


def save_file_locally(file_name, file_bytes):
    file_path=f'./doc_store/{file_name}'
    with open(file_path, 'wb') as f: 
        f.write(file_bytes)
    if os.path.isfile(file_path):
        return file_path
    
def save_file_chunks(file_name, file_bytes, open_api_key, chunk_size=config.CHUNK_SIZE, model=config.OPENAI_EMBEDDING_MODEL):
    #ref the raft codebase 
    try:
        file_name = file_name.lower()
        if file_name[-4:] == '.pdf':
            text = ""
            reader = PyPDF2.PdfReader(file_bytes)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text()
        elif file_name[-7:] == '.manual' or file_name[-4:] == '.txt':
            text = str(file_bytes.read().decode())
        else: 
            raise TypeError("Document is not one of the accepted types: pdf, txt")

        num_chunks = ceil(len(text) / chunk_size)
        embeddings =  OpenAIEmbeddings(openai_api_key=open_api_key, model=model)
        text_splitter = SemanticChunker(embeddings, number_of_chunks=num_chunks)
        chunks = text_splitter.create_documents([text])
        chunks = [chunk.page_content for chunk in chunks]
        embeddings_list = langchain_utils.get_open_ai_embeddings_docs(chunks)
        if pgvector_utils.insert_file_chunks_into_db([(file_name, chunk_text, embedding) for (embedding, chunk_text) in zip(embeddings_list, chunks)]):
            return file_name 
    except Exception as e:
        print(f'ERROR saving file to DB: {e}')

if __name__ == '__main__':
    pass 