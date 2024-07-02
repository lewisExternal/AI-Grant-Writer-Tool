import requests 
import streamlit as st 
import re 

import utils.config as config 

def parse_result_helper(response:object, default:dict={})->dict:
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Status code {response.status_code} ', icon="🚨")
        return default

def get_all_records(table_name:str)->object:
    try:
        data = {"text":table_name}
        if response := requests.post(f'{config.FASTAPI_URL}get_data',json=data):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR get_all_records: {e}')

def get_questions(selected_project:dict)->object:
    try:
        data = {"project_id":str(selected_project.get('id'))}
        if response := requests.get(f'{config.FASTAPI_URL}get_questions',params=data):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR get_questions: {e}')

def insert_file(filename:str,file:object)->int:
    try:
        files = {'file': file.getvalue()}
        data = {'file_name':filename}
        response = requests.post(f'{config.FASTAPI_URL}file_upload',files=files,data=data)
        return response.status_code
    except Exception as e:
        print(f'ERROR insert_file: {e}')

def insert_file_v2(filename:str,file:object)->int:
    try:
        files = {'file': file.getvalue()}
        data = {'file_name':filename}
        response = requests.post(f'{config.FASTAPI_URL}file_upload_chunks',files=files,data=data)
        return response.status_code
    except Exception as e:
        print(f'ERROR insert_file_v2: {e}')

def format_file_name(file_name):
    file_name = file_name.lower()
    # file_name = re.sub(r"^\s+", "", file_name, flags = re.MULTILINE)
    file_name = file_name.split('.')[0]
    file_name = "_".join(file_name.split(' ')[:5])
    return file_name

def insert_text_snippet(text:str)->int:
    try:
        files = {'file': bytes(text, 'utf-8')}
        data = {'file_name':f"{format_file_name(text)}.manual"}
        response = requests.post(f'{config.FASTAPI_URL}file_upload_chunks',files=files,data=data)
        return response.status_code
    except Exception as e:
        print(f'ERROR insert_text_snippet: {e}')

def insert_project(project_name:str, project_description:str)->object:
    try:
        data = {'project_name':project_name, 'project_description':project_description}
        if response := requests.post(f'{config.FASTAPI_URL}create_project',params=data):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR: {e}')

def save_questions(questions:list[dict],selected_project:dict)->object:
    try:
        project_id = selected_project.get('id')
        data = {'questions': questions}
        params = {'project_id':project_id}
        if response := requests.post(f'{config.FASTAPI_URL}save_questions', json=data, params=params):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR save_questions: {e}')

def check_open_ai_credentials()->object:
    try:
        if response := requests.get(f'{config.FASTAPI_URL}check_credentials'):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR check_open_ai_credentials: {e}')

def get_openai_embeddings(text:str)->object:
    try:
        data = {"text":text}
        if response := requests.post(f'{config.FASTAPI_URL}get_embeddings',json=data):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR get_openai_embeddings: {e}')

def ask_rag_question(question:list)->object:
    try:
        data = {"question":question[1]}
        if response := requests.post(f'{config.FASTAPI_URL}ask_auto_gen_question',data=data):
            return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR ask_rag_question: {e}')        

def ask_group_chat(qa_problem:str, context:str)->object:
    try:
        data = {"qa_problem":qa_problem, "context":context}
        if response := requests.post(f'{config.FASTAPI_URL}construct_agent_group_chat',data=data):
           return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR ask_group_chat: {e}')        

def construct_agent()->object: 
    try:
        if (file_paths := st.session_state.get('selected_files')) and (project_name := st.session_state.get('selected_project')):
            data = { "file_paths":file_paths, "project_name":project_name}
            if response := requests.post(f'{config.FASTAPI_URL}construct_agent',data=data):
                return parse_result_helper(response)
    except Exception as e:
        print(f'ERROR construct_agent: {e}')    

def get_rag_context(question:list, files:list)->object:
    try:
        data = {"question":str(question[4]), "files":files}
        if response := requests.post(f'{config.FASTAPI_URL}get_rag_context',data=data):
            return parse_result_helper(response, '')
    except Exception as e:
        print(f'ERROR get_rag_context: {e}')   

if __name__ == "__main__":
    pass 
