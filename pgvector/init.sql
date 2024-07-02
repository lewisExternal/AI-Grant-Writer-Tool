CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  name text,
  description text,
  created_at timestamptz DEFAULT now()
);

INSERT INTO projects (name, description) VALUES ('Project A','I am A test description');
INSERT INTO projects (name, description) VALUES ('Project B','I am B test description');

CREATE TABLE IF NOT EXISTS questions (
  id SERIAL PRIMARY KEY,
  question text,
  answer text,
  project_id int,
  embedding vector,
  chat_history text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS files (
  id SERIAL PRIMARY KEY,
  file_name text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS file_chunks (
  id SERIAL PRIMARY KEY,
  file_name text,
  chunk_text text,
  embedding vector,
  created_at timestamptz DEFAULT now()
);
