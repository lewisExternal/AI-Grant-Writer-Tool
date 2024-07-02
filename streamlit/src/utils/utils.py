import requests 
import streamlit as st 
from streamlit_js_eval import streamlit_js_eval
import ast  
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool


import utils.config as config 
import utils.fast_api_utils as fast_api_utils  

def submit_manual_text():
    if manual_text := st.session_state.get('manual_text'):
        if fast_api_utils.insert_text_snippet(manual_text) == 200:
            delete_list_from_state_helper(['files','questions','projects'])
            streamlit_js_eval(js_expressions="parent.window.location.reload()")           

def delete_list_from_state_helper(var_list):
    for item in var_list:
        if item in st.session_state:
            del st.session_state[item]

def submit_files():
    if file := st.session_state.get('submit_files' ):
        if fast_api_utils.insert_file_v2(file.name,file) == 200:
            delete_list_from_state_helper(['files','questions','projects'])
            streamlit_js_eval(js_expressions="parent.window.location.reload()")

def add_question_helper(project_dict, new_question):
    if selected_project := st.session_state.get('selected_project'):
        if project := project_dict[selected_project]:
            project_id = project.get('id')
            if new_question and project_id:
                if embedding := fast_api_utils.get_openai_embeddings(new_question) or None: 
                    embedding = str(embedding)
                    st.session_state.questions.append([None, new_question, '', project_id, embedding, '', None])

def construct_dict_helper(question):
    result = {}
    fields = ['question','answer','project_id','embedding','chat_history']
    for ix, field in enumerate(fields):
        if field == 'embedding':    
            if embedding := question[ix + 1]:
                result[field] = str(embedding) #ast.literal_eval(embedding) 
            else:
                if embedding := fast_api_utils.get_openai_embeddings(question[1]):
                    result[field] = str(embedding)
        else:
            result[field] = question[ix + 1]
    return result

def format_questions(questions):
    return [construct_dict_helper(question) for question in questions]

def remove_question_from_list(ix,questions,selected_project):
    del questions[ix]
    st.session_state['questions'] = questions 
    if selected_project:
        if response := fast_api_utils.save_questions(questions,selected_project) and response.get('result'):
            st.toast('Questions saved!')
    st.rerun()

def handle_project():
    if st.session_state.get('project_name') and st.session_state.get('project_description'):
        fast_api_utils.insert_project(st.session_state.project_name, st.session_state.project_description)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

def ask_rag_question_update_questions(questions, ix):
    if response := fast_api_utils.ask_rag_question(questions[ix]):
        questions[ix][2] = response[0]
        st.session_state['questions'] = questions 
        st.rerun() 

def parse_chat_history(chat_history):
    text = ''
    for response in chat_history:
        text += f"role: {response.get('role','')} \n\n"
        text += f"content:\n\n{response.get('content','')} \n\n"
        text += f"*"*10 + '\n\n'
    return text 

def ask_rag_question_update_questions_v2(questions, ix, files):
    if not (embedding := questions[ix][4]):
        if embedding := fast_api_utils.get_openai_embeddings(questions[ix][1]):
            questions[ix][4] = embedding
    rag_context = 'None'
    if files:
        rag_context = fast_api_utils.get_rag_context(questions[ix],files)
    if response := fast_api_utils.ask_group_chat(questions[ix][1], rag_context):
        questions[ix][2] = response.get('summary','')
        questions[ix][5] = parse_chat_history(response.get('chat_history',[]))
        st.session_state['questions'] = questions 
        st.rerun()

def get_data_from_db(projects,files,credentials):
    if (not projects) or (not files) or (not credentials):
        pool = Pool()
        processes = [pool.apply_async(fast_api_utils.get_all_records,args=('projects',)), pool.apply_async(fast_api_utils.get_all_records,args=('files',)), pool.apply_async(fast_api_utils.check_open_ai_credentials)]
        [process.wait() for process in processes]
        results = [process.get() for process in processes]
        st.session_state['projects'] = results[0]
        st.session_state['files'] = results[1]
        st.session_state['credentials'] = results[2]

def handle_project_select_callback():
    if st.session_state.get('questions'):
        del st.session_state['questions']

if __name__ == "__main__":
    pass 