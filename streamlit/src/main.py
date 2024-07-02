import streamlit as st  
import os 
import asyncio 

import utils.utils as utils  
import utils.fast_api_utils as fast_api_utils  
import utils.fe_utils as fe_utils 

def main():
    st.title('AI Grant Writer')

    utils.get_data_from_db(st.session_state.get('projects'),st.session_state.get('files'),st.session_state.get('credentials'))

    fe_utils.check_credentials()

    tab1, tab2 = st.tabs(['Upload Supporting Files/ Text', 'Generate Text'])

    with tab1: 

        st.header('Upload a file', anchor='upload-a-file')
        with st.form('Manual File Upload'):
            st.file_uploader('Please upload your files',type=['pdf', 'txt'], key='submit_files' ) 
            st.form_submit_button('Submit', on_click=utils.submit_files)    
             
        st.header('Manual text upload ')
        with st.form('Manual Text Upload'):
            st.text_area('Please add supporting text ', key='manual_text')
            st.form_submit_button('Submit', on_click=utils.submit_manual_text)

    with tab2:

        # init 
        project_dict = None 
        
        st.header('Create project', anchor='create-project')
        with st.form("my_form"):
            st.text_input('Add your project name here', key='project_name')
            st.text_area('Add your project description here', key='project_description')
            if st.form_submit_button("Submit"):
                utils.handle_project() 

        st.header('Select files', anchor='select-a-file')
        if st.session_state.get('files'):
            st.multiselect('Select your files',[x[1] for x in st.session_state.files],key='selected_files')
        else:
            st.write('No files found, please upload a file on the prior tab "Upload Supporting Files/ Text". ')

        if st.session_state.get('projects'):
            st.header('Select project')
            project_dict = {x[1]:{'id':x[0], 'name':x[1], 'description':x[2]} for x in st.session_state.projects}
            st.selectbox('Select your project',project_dict.keys(),on_change=utils.handle_project_select_callback,key='selected_project')
            if selected_project := st.session_state.get('selected_project'):
                st.write(f'Project Description: \n\n  {project_dict.get(selected_project,{}).get("description","")}')
        
        if (selected_project := st.session_state.get('selected_project')) and project_dict and (not st.session_state.get('questions')):
            st.session_state['questions'] = fast_api_utils.get_questions(project_dict[selected_project]) 

        st.header('Input Questions ')
        if st.session_state.get('questions'):
            if not st.session_state.get('selected_files'): 
                st.write('No source files selected, please select a file for reference.')
                st.markdown("[Select a file](#select-a-file)")
            fe_utils.render_questions(st.session_state.get('questions'), st.session_state.get('selected_files',[]), project_dict[st.session_state.selected_project])
        else: 
            st.write('No questions found. Please add a question.')

        st.header('Add question')
        with st.form("add_question_form"):
            new_question = st.text_area('Add question here', height=200)
            if st.form_submit_button("Submit"):
                utils.add_question_helper(project_dict, new_question)

        if st.session_state.get('questions'):
            st.header('Save to database')
            if st.button('Save questions to DB'):
                with st.spinner(text="In progress..."):
                    parsed_questions = utils.format_questions(st.session_state.questions)
                    if (response := fast_api_utils.save_questions(parsed_questions,project_dict[st.session_state.selected_project])) and response.get('result'):
                        st.toast('Questions saved!')

    


if __name__ == '__main__':
    main()