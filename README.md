# AI-Grant-Writer-Tool
An open-source AI tool for writing grant applications, using Microsoft AutoGen combined with Retrieval-Augmented Generation (RAG) via a vector database in PostgreSQL/ pgvector and LangChain - served in FastAPI/ Streamlit. Dockerised to run locally.

Writing grant applications can be time consuming and tedious, Generative AI seems like a natural solution though naive approaches can be limited in their efficacy.   

Through this system, we add user submitted context through Retrieval Augmented Generation (RAG), then further optimize results through a multi agent approach to review output from legal, ethical and grant writing agents.    

## What is AutoGen?
"AutoGen provides a multi-agent conversation framework as a high-level abstraction. It is an open-source library for enabling next-generation LLM applications with multi-agent collaborations, teachability and personalization. With this framework, users can build LLM workflows. The agent modularity and conversation-based programming simplifies development and enables reuse for developers. End-users benefit from multiple agents independently learning and collaborating on their behalf, enabling them to accomplish more with less work. Benefits of the multi agent approach with AutoGen include agents that can be backed by various LLM configurations; native support for a generic form of tool usage through code generation and execution; and, a special agent, the Human Proxy Agent that enables easy integration of human feedback and involvement at different levels." - [AutoGen Website](https://www.microsoft.com/en-us/research/project/autogen/)

## What is Retrieval-Augmented Generation?
"Retrieval-Augmented Generation (RAG) is the process of optimizing the output of a large language model, so it references an authoritative knowledge base outside of its training data sources before generating a response. Large Language Models (LLMs) are trained on vast volumes of data and use billions of parameters to generate original output for tasks like answering questions, translating languages, and completing sentences. RAG extends the already powerful capabilities of LLMs to specific domains or an organization's internal knowledge base, all without the need to retrain the model. It is a cost-effective approach to improving LLM output so it remains relevant, accurate, and useful in various contexts." - [AWS Website](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

![image_1](https://github.com/lewisExternal/AI-Grant-Writer-Tool/assets/81447748/eb5fd739-ee93-4735-9c74-9e60359e536c)

Read the Medium article [here](TBD) 

## Run Locally  

### Run the Streamlit application  
First, you must add your Open AI API key.  
```
./config/.env
```
Run the following from the root directory.  
```
docker compose up --build 
```
To see the Streamlit application, please navigate to:  
```
http://localhost:8501/
```
Once finished, be sure to run the following.
```
docker compose down
```

## Requirements  
Requires the following 
* docker desktop 
* Open AI API Key 

## References 
* https://arxiv.org/pdf/2308.08155
* https://arxiv.org/pdf/2403.10131

