import json
import os
import chromadb
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.retrieve_utils import TEXT_FORMATS
import json
import re 

env_var_dict = [
    {
        'model': 'gpt-4',
        'api_key': os.environ.get('OPENAI_API_KEY','')
    },
    {
        'model': 'gpt-3.5-turbo',
        'api_key': os.environ.get('OPENAI_API_KEY','')
    }
]

env_var = json.dumps(env_var_dict)

os.environ["AUTO_GEN_CONFIG"] = env_var

config_list = autogen.config_list_from_json(
    env_or_file='AUTO_GEN_CONFIG',
    filter_dict={
        "model": {
            "gpt-4",
            "gpt4",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-v0314",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-0301",
            "chatgpt-35-turbo-0301",
            "gpt-35-turbo-v0301",
            "gpt",
        }
    }
)

config_list = autogen.config_list_from_json(env_or_file="AUTO_GEN_CONFIG")

assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    },
)

ragproxyagent = None 

def construct_rag_proxy_agent(file_paths):
    file_path_full = [f'./doc_store/{file}' for file in file_paths]
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "get_or_create": True,
            "update_context": False,
            "task": "default",
            "docs_path": file_path_full,
            "custom_text_types": ["non-existent-type"],
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="./output/chromadb"),  # deprecated, use "vector_db" instead
            "vector_db": None,  # to use the deprecated `client` parameter, set to None and uncomment the line above
            "overwrite": False,  # set to True if you want to overwrite an existing collection
        },
        code_execution_config=False,  # set to False if you don't want to execute the code
    )
    return ragproxyagent

def ask_rag_question(qa_problem,file_paths):
    assistant.reset()
    ragproxyagent = construct_rag_proxy_agent(file_paths)
    if res := ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem):
        try:
            if text := res.chat_history[0].get('content'):
                context = re.sub(r"(.*)context is:", "", text ,flags= re.DOTALL | re.IGNORECASE | re.MULTILINE)
        except Exception as e:
            print(f'ERROR: {e}')
        return res.summary, context 

def format_project_name_helper(text):
    text = text.lower()
    text = text.replace(' ','_')
    ''.join([i for i in text if i.isalpha() or i =='_'])
    return text

def construct_rag_proxy_agent_pgvector(file_paths,project_name):
    try:
        global ragproxyagent 
        file_path_full = [f'./doc_store/{file}' for file in file_paths]
        project_name = format_project_name_helper(project_name)
        ragproxyagent = RetrieveUserProxyAgent(
            name="ragproxyagent",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "default",
                "update_context": False, 
                "docs_path": file_path_full,
                "custom_text_types": ["non-existent-type"],
                "chunk_token_size": 4000,
                "model": config_list[0]["model"],
                "vector_db": "pgvector",  # PGVector database
                "collection_name": project_name,
                "db_config": {
                    "connection_string": "postgresql://testuser:testpwd@localhost:5432/vectordb",  # Optional - connect to an external vector database
        #             "host": "localhost", # Optional vector database host
        #             "port": 5432, # Optional vector database port
        #             "database": "vectordb", # Optional vector database name
        #             "username": "testuser", # Optional vector database username
        #             "password": "testpwd", # Optional vector database password
                    "model_name": "all-MiniLM-L6-v2",  # Sentence embedding model from https://huggingface.co/models?library=sentence-transformers or https://www.sbert.net/docs/pretrained_models.html
                },
                "get_or_create": True,  # set to False if you don't want to reuse an existing collection
                "overwrite": True,  # set to True if you want to overwrite an existing collection
            },
            code_execution_config=False,  # set to False if you don't want to execute the code
        )
        return True 
    except Exception as e:
        print(f'ERROR construct_rag_proxy_agent_pgvector: {e}')

def ask_rag_question_pgvector(qa_problem):
    assistant.reset()
    # ragproxyagent = construct_rag_proxy_agent_pgvector(file_paths,project_name)
    if ragproxyagent:
        if res := ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem):
            try:
                if text := res.chat_history[0].get('content'):
                    if context := re.sub(r"(.*)context is:", "", text ,flags= re.DOTALL | re.IGNORECASE | re.MULTILINE):
                        return res.summary, context 
            except Exception as e:
                print(f'ERROR: {e}')
    return None, None 

def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

#init agents 
writer = autogen.AssistantAgent(
    name="Writer",
    system_message="You are a writer. You write professional grant applications. " 
        "Answer the question based on the context if it exists. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    llm_config=env_var_dict[0],
)

critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=env_var_dict[0],
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the application.",
)

grant_reviewer = autogen.AssistantAgent(
name="Grant application Reviewer",
llm_config=env_var_dict[0],
system_message="You are an grant application reviewer, known for "
    "your ability to optimize content for grant applications, "
    "giving the application the maximum probability of being successful. " 
    "Make sure your suggestion is concise (within 3 bullet points), "
    "concrete and to the point. "
    "Begin the review by stating your role.",
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal Reviewer",
    llm_config=env_var_dict[0],
    system_message="You are a legal reviewer, known for "
        "your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

ethics_reviewer = autogen.AssistantAgent(
name="Ethics Reviewer",
llm_config=env_var_dict[0],
system_message="You are an ethics reviewer, known for "
    "your ability to ensure that content is ethically sound "
    "and free from any potential ethical issues. " 
    "Make sure your suggestion is concise (within 3 bullet points), "
    "concrete and to the point. "
    "Begin the review by stating your role. ",
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta Reviewer",
    llm_config=env_var_dict[0],
    system_message="You are a meta reviewer, you aggragate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

def ask_rag_question_minimal_feedback(qa_problem, context):
    if res := critic.initiate_chat(
        recipient=writer,
        message=qa_problem,
        max_turns=2,
        summary_method="last_msg"
    ): 
        return res.summary


def ask_rag_question_maximum_feedback(qa_problem, context):

    # init results 
    summary, chat_history =  '', ''
    
    qa_problem = f'<question>{qa_problem}<question>'

    if context and context != 'None':
        qa_problem = f'<context>{context}<context>{qa_problem}'
    
    review_chats = [
        {
         "recipient": grant_reviewer, 
         "message": reflection_message, 
         "summary_method": "reflection_with_llm",
         "summary_args": {"summary_prompt" : 
            "Return review into as JSON object only:"
            "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
         "max_turns": 1},
        {
        "recipient": legal_reviewer, "message": reflection_message, 
         "summary_method": "reflection_with_llm",
         "summary_args": {"summary_prompt" : 
            "Return review into as JSON object only:"
            "{'Reviewer': '', 'Review': ''}.",},
         "max_turns": 1},
        {"recipient": ethics_reviewer, "message": reflection_message, 
         "summary_method": "reflection_with_llm",
         "summary_args": {"summary_prompt" : 
            "Return review into as JSON object only:"
            "{'reviewer': '', 'review': ''}",},
         "max_turns": 1},
         {"recipient": meta_reviewer, 
          "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.", 
         "max_turns": 1},
    ]

    critic.register_nested_chats(
    review_chats,
    trigger=writer,
    )
    
    if res := critic.initiate_chat(
        recipient=writer,
        message=qa_problem,
        max_turns=2,
        summary_method="last_msg"
    ):
        summary, chat_history = res.summary, res.chat_history
    return summary, chat_history 

if __name__ =="__main__":
    pass 