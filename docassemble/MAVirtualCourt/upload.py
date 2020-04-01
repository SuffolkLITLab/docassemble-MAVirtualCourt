from datetime import datetime
from docassemble.base.util import get_config
from psycopg2 import connect

__all__ = ["initialize_db", "new_entry"]

db_config = get_config("filesdb")

def initialize_db():
  """
  Initialize the postgres tables for courts and files.
  We expect to have an entry 'filesdb' in the main configuration yaml.
  Below is a sample config:
  
  filesdb:
    database: uploads
    user: uploads
    password: Password1!
    host: localhost
    port: 5432
    
  This user should have access to the database (read, write)
  """
  conn = connect(**db_config)
  cur = conn.cursor()

  # creates a courts table. currently just maps name to email
  cur.execute("""
  CREATE TABLE IF NOT EXISTS courts(
    court_name    TEXT PRIMARY KEY,
    court_email   TEXT NOT NULL 
  );
  """)

  # creates a files table. has time name, document name, court name, and path
  # in the future, we can filter by visibility on the court-basis
  cur.execute("""
  CREATE TABLE IF NOT EXISTS files(
    id           SERIAL       PRIMARY KEY,
    timestamp    TIMESTAMPTZ  NOT NULL,
    name         TEXT         NOT NULL,
    doc_name     TEXT         NOT NULL,
    court_name   TEXT         REFERENCES courts(court_name),
    file_path    TEXT         NOT NULL
  );
  """)

  conn.commit()
  cur.close()
  conn.close()
  
def new_entry(name="", doc_name="", court_name="", file_path=""):
  """
  Creates a new upload entry in the database
  
  Args:
    name (str): the name of who is completing the form
    doc_name (str): the name of the document
    court_name (str): the name of the court to file
    file_path (str): the path of the assembled file (on disk)
  """
  conn = connect(**db_config)
  cur = conn.cursor()
  
  cur.execute("SELECT * from courts WHERE court_name = %s", (court_name,))
  courts_list = cur.fetchall()
  
  if len(courts_list) == 0:
    cur.close()
    conn.close()
    # in our system, this should never happen, but will leave in for debugging
    raise ValueError(f"Court {court_name} does not exist")
  
  cur.execute("INSERT INTO files (timestamp, name, doc_name, court_name, file_path) VALUES (%s, %s, %s, %s, %s)", (datetime.now(), name, doc_name, court_name, file_path))
  
  conn.commit()
  cur.close()
  conn.close()