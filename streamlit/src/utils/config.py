import os 

DOCKER_RUNNING = os.environ.get('DOCKER_RUNNING', False)

FASTAPI_URL='http://localhost:80/'
if DOCKER_RUNNING:
    FASTAPI_URL='http://fastapi:80/'


if __name__ =="__main__":
    pass 