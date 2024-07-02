import os 

DOCKER_RUNNING = os.environ.get('DOCKER_RUNNING', False)

DB_HOSTNAME='localhost'
if DOCKER_RUNNING:
    DB_HOSTNAME='db'

OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'

CHUNK_SIZE = 4000

ERROR_MESSAGE = "Internal server error. "

if __name__ =="__main__":
    pass 