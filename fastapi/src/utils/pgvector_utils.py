import psycopg2

# local imports 
try:
    import src.utils.config as config
except Exception as e:
    import utils.config as config

conn = psycopg2.connect(
host=config.DB_HOSTNAME, 
database="vectordb",
user="testuser",
password="testpwd"
)

def get_embeddings():
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT * 
        FROM embeddings
        """)

        results = cur.fetchall()
        for row in results:
            print(f"Name: {row[0]}, Similarity: {row[1]}")
        cur.close()
    except Exception as e:
        print(f'ERROR get_embeddings: {e}')
        conn.rollback()

def query_data(table_name):
    try:
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * 
        FROM {table_name}
        """)
        results = cur.fetchall()
        cur.close()
        return results 
    except Exception as e:
        print(f'ERROR query_data: {e}')
        conn.rollback()
        return False 

def query_questions(project_id):
    try:
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * 
        FROM questions
        WHERE project_id = {project_id}
        """)
        results = cur.fetchall()
        cur.close()
        return results 
    except Exception as e:
        print(f'ERROR query_questions: {e}')
        conn.rollback()
        return False 

def insert_file(filename):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO files (file_name) VALUES (%s)", (filename,)) 
        conn.commit()
        cur.close()
        return True 
    except Exception as e:
        print(f'ERROR insert_file: {e}')
        conn.rollback()        

def insert_project(project_name, project_description):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO projects (name, description) VALUES (%s,%s)", (project_name,project_description,)) 
        conn.commit()
        cur.close()
        return True 
    except Exception as e:
        print(f'ERROR insert_project: {e}')
        conn.rollback()        

def delete_questions_from_db(project_id):
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM questions WHERE project_id = {project_id}") 
        conn.commit()
        cur.close()
        return True 
    except Exception as e:
        print(f'ERROR delete_questions_from_db: {e}')
        conn.rollback()     
        return False 

def insert_questions_into_db(questions):
    try:
        cur = conn.cursor()
        for question in questions.questions:
            cur.execute(f"INSERT INTO questions (question, answer, project_id, embedding, chat_history) VALUES ('{escape_single_quote_helper(question.question)}', '{escape_single_quote_helper(question.answer)}', {question.project_id}, '{question.embedding}', '{escape_single_quote_helper(question.chat_history)}');") 
        conn.commit()
        cur.close()
        return True 
    except Exception as e:
        print(f'ERROR insert_questions_into_db: {e}')
        conn.rollback()    
        return False  

def escape_single_quote_helper(text):
    return text.replace("'","''")

def insert_file_chunks_into_db(chunks):
    try:
        cur = conn.cursor()
        for file_name, chunk_text, embedding in chunks:
            cur.execute(f"INSERT INTO file_chunks (file_name, chunk_text, embedding) VALUES ('{escape_single_quote_helper(file_name)}', '{escape_single_quote_helper(chunk_text)}', '{embedding}');") 
        conn.commit()
        cur.close()
        return True 
    except Exception as e:
        print(f'ERROR insert_file_chunks_into_db: {e}')
        conn.rollback()    
    return False  

def save_questions(project_id, questions):
    if delete_questions_from_db(project_id):
        return insert_questions_into_db(questions) 

def rag_context(question, files):
    try:
        file_names = ','.join([f"'{x}'" for x in files])
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * 
        FROM file_chunks
        WHERE file_name in ({file_names})
        ORDER BY embedding <-> '{question}'
        LIMIT 1;
        """)
        rag_context = None 
        if results := cur.fetchall():
            rag_context = results[0][2]
        cur.close()
        if rag_context:
            return rag_context 
    except Exception as e:
        print(f'ERROR rag_context: {e}')
        conn.rollback()

if __name__ == "__main__":
    pass 