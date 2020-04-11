from datetime import datetime
from docassemble.base.functions import defined, get_user_info
from docassemble.base.util import get_config, send_email, user_info
from psycopg2 import connect
from textwrap import dedent

__all__ = ["initialize_db", "new_entry", "send_attachments"]

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

  # creates a interviews table. has time name, document name, court name
  # in the future, we can filter by visibility on the court-basis
  cur.execute("""
  CREATE TABLE IF NOT EXISTS interviews(
    id           SERIAL        PRIMARY KEY,
    timestamp    TIMESTAMPTZ   NOT NULL,
    name         TEXT          NOT NULL,
    court_name   TEXT          NOT NULL,
    user_id      VARCHAR(50)   NOT NULL
  );
  """)
  
  # creates a files table. This stores important metadata for accessing files
  cur.execute("""
  CREATE TABLE IF NOT EXISTS files(
    id             SERIAL        PRIMARY KEY,
    number         TEXT          NOT NULL,
    filename       TEXT          NOT NULL,
    sensitive      BOOLEAN       NOT NULL DEFAULT FALSE,
    mimetype       VARCHAR(30)   NOT NULL,
    submission_id  INTEGER       REFERENCES interviews(id)
  );
  """)

  conn.commit()
  cur.close()
  conn.close()
  
def get_user_id():
  """
  Returns a unique ID for the current user
  If the user is logged in, uses their user id, otherwise uses session id.
  """
  info = get_user_info()
  
  if info:
    return info["id"]
  else:
    return user_info().session  

def new_entry(name="", court_name="", court_emails=dict(), files=[]) -> str:
  """
  Creates a new upload entry in the database
  
  Args:
    name (str): the name of who is completing the form
    doc_name (str): the name of the document
    court_name (str): the name of the court to file
    file_path (str): the path of the assembled file (on disk)
  """
  if court_name not in court_emails:
    # in our system, this should never happen, but will leave in for debugging
    raise ValueError(f"Court {court_name} does not exist")

  connection = connect(**db_config)
  submission_id = None
  
  with connection.cursor() as cursor:
    cursor.execute("INSERT INTO interviews (timestamp, name, court_name, user_id) VALUES (%s, %s, %s, %s) RETURNING id", (datetime.now(), name, court_name, get_user_id()))
    submission_id = cursor.fetchone()[0]

    for file in files:
      sensitive = defined("file.sensitive") and file.sensitive
      cursor.execute("INSERT INTO files (number, filename, mimetype, sensitive, submission_id) VALUES (%s, %s, %s, %s, %s)", (file.number, file.filename, file.mimetype, sensitive, submission_id))
    
  connection.commit()  
  connection.close()
  
  return str(submission_id)

def send_attachments(name="", court_name="", court_emails=dict(), files=[], submission_id=""):
  if court_name not in court_emails:
    # in our system, this should never happen, but will leave in for debugging
    raise ValueError(f"Court {court_name} does not exist")

  attachments = [file for file in files if not defined("file.sensitive") or not file.sensitive]
  court_email = court_emails[court_name]

  filenames = [file.filename for file in attachments]
  filenames_str = "\n".join(filenames)

  if len(attachments) != len(files):
    if len(attachments) == 0:
      body = dedent(f"""
      Dear {court_name}:

      {name} has submitted {len(files)} online. However, these file(s) have sensitive information, and will not be sent over email.
      
      Please access these forms with the following submission id: {submission_id}.
      """)

      attachments = None
    else:
      body = dedent(f"""
      Dear {court_name}:
      
      You are receiving {len(attachments)} files from {name}:
      {filenames_str}

      However, there are also {len(files) - len(attachments)} forms which are sensitive that will not be sent over email.

      Please access these forms with the following submission id: {submission_id}.
      """)
  else:
    body = dedent(f"""
    Dear {court_name}:

    You are receiving {len(attachments)} files from {name}:
    {filenames_str}

    The reference ID for these forms is {submission_id}.
    """)

  return send_email(to=court_email, subject=f"Online form submission {submission_id}", body=body, attachments=attachments)