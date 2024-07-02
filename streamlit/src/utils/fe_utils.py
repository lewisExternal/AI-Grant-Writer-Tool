import streamlit as st

import utils.utils as utils  
import utils.fast_api_utils as fast_api_utils  

@st.experimental_dialog("Chat history")
def display_message_dialog(text):
    st.write(text)

def render_questions(questions,files,selected_project):
    if questions:
        for ix, question in enumerate(questions):
            with st.expander(f"{ix+1}\. {question[1]}",expanded=True):
                st.text_area('Write your answer here',value=question[2], key=f'question_{ix}', height=200)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button('Generate response', key=f'gen_button_{ix}'):
                        with st.spinner('Running...'):
                            utils.ask_rag_question_update_questions_v2(questions, ix, files)
                with col2:
                    if st.button('Display chat history', key=f'chat_history_button_{ix}'):
                        display_message_dialog(question[5])   
                with col3:
                    if st.button('Delete question', key=f'delete_button_{ix}'):
                        utils.remove_question_from_list(ix,questions,selected_project) 

def check_credentials(): 
    if st.session_state.get('credentials') != 'OK':
            st.write('Please provide your OPEN API KEY in the config ( ./config/.env ) and restart ')
            st.stop()


if __name__ == "__main__":
    pass 
