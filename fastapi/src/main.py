from fastapi import FastAPI, UploadFile, File, Form, UploadFile, HTTPException, status
from pydantic import BaseModel
from typing import List, Annotated, Union, Set
import uvicorn
import os 

open_api_key = os.environ.get('OPENAI_API_KEY')

# local imports 
try:
    import src.utils.pgvector_utils as pgvector_utils
    import src.utils.langchain_utils as langchain_utils
    import src.utils.auto_gen_utils as auto_gen_utils
    import src.utils.utils as utils
    import src.utils.config as config
except Exception as e:
    print(f'ERROR: {e}')
    import utils.pgvector_utils as pgvector_utils
    import utils.langchain_utils as langchain_utils
    import utils.auto_gen_utils as auto_gen_utils
    import utils.utils as utils
    import utils.config as config


description = '''
API for AI grant writing. 🧠
'''
app = FastAPI(description=description)

class Text(BaseModel):
    text: str

class Question(BaseModel):
    question: str
    answer: str
    project_id: int 
    embedding: str
    chat_history: str

class Questions(BaseModel):
    questions: List[Question]

@app.get("/healthcheck")
async def root():
    '''healthcheck endpoint'''
    return 'OK'

@app.get("/check_credentials")
async def check_credentials():
    '''check Open AI credentials have been added to the config'''
    if open_api_key!='PLACE_YOUR_KEY_HERE':
        return 'OK' 

@app.post("/create_project")
async def create_project(project_name: str, project_description:str):
    '''create project in DB'''
    if pgvector_utils.insert_project(project_name, project_description):
        return {"projectName": project_name}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/file_upload")
async def file_upload(file_name: Annotated[str, Form()], file: List[UploadFile]):
    '''upload file to the DB'''
    file_bytes=file[0].file.read()
    if file_path := utils.save_file_locally(file_name,file_bytes):
        if pgvector_utils.insert_file(file_name,file_path):
            return {"filename": file_name}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/file_upload_chunks")
async def file_upload_chunks(file_name: Annotated[str, Form()], file: List[UploadFile]):
    '''upload file to the DB split into chunks'''
    file=file[0].file 
    if file_name := utils.save_file_chunks(file_name, file, open_api_key):
        if pgvector_utils.insert_file(file_name):
            return {"filename": file_name}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/get_data")
def get_data_from_db(text: Text):
    '''return all records from a given table'''
    result = pgvector_utils.query_data(text.text)
    if result != False:
        return result
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.get("/get_questions")
def get_questions_from_db(project_id: str):
    '''return all questions for a given project_id'''
    result = pgvector_utils.query_questions(project_id)
    if result != False:
        return result
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/save_questions")
def save_questions_to_db(project_id: str, questions: Questions):
    '''insert questions into DB'''
    if result := pgvector_utils.save_questions(project_id, questions):
        return {'result':result}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/get_embeddings")
def open_ai_embeddings(text: Text):
    '''return embeddings from text'''
    if result := langchain_utils.get_open_ai_embeddings(text.text):
        return result 
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

# @app.post("/get_embeddings")
# def read_item():
#     result = pgvector_utils.get_embeddings()
#     return result 

# @app.post("/manage_file_dir")
# def manage_file_dir(files: List[str]):
#     return auto_gen_utils.manage_file_dir(files) 

@app.post("/ask_auto_gen_question")
def ask_rag_question(question: Annotated[str, Form()]):
    '''ask question via rag agent'''
    res, context = auto_gen_utils.ask_rag_question_pgvector(question)
    if res and context:
        return res, context
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/construct_agent")
def construct_agent(file_paths: Annotated[List[str], Form()], project_name: Annotated[str, Form()]):
    '''initialize rag proxy agent'''
    if auto_gen_utils.construct_rag_proxy_agent_pgvector(file_paths,project_name):
        return {}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/construct_agent_group_chat")
def construct_agent(qa_problem: Annotated[str, Form()], context: Annotated[str, Form()]):
    '''construct multi agent autogen answer for question and context'''   
    summary, chat_history = auto_gen_utils.ask_rag_question_maximum_feedback(qa_problem, context)
    if summary and chat_history:
        return {"summary":summary, "chat_history":chat_history} 
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

@app.post("/get_rag_context")
def get_rag_context(question: Annotated[str, Form()], files: Annotated[List[str], Form()]):
    '''get rag context from question given file list '''
    if result := pgvector_utils.rag_context(question, files):
        return result 
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=config.ERROR_MESSAGE)

if __name__ == "__main__":
    # src.main:app --proxy-headers --host 0.0.0.0 --port 80 
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)