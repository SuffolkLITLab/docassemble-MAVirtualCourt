from datetime import datetime
from docassemble.base.core import DAFile
from docassemble.base.functions import defined, get_user_info, interview_url, quantity_noun
from docassemble.base.util import get_config, send_email, user_info
from psycopg2 import connect
from textwrap import dedent
from typing import Optional, Tuple

__all__ = [
  "can_access_submission",
  "get_accessible_submissions",
  "get_files",
  "initialize_db",
  "new_entry",
  "reverse_dictionary",
  "send_attachments",
  "url_for_submission"
]

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
  
def reverse_dictionary(input_dict: {}) -> dict:   
  """Creates a dictionary mapping values to keys"""
  return { value: key for key, value in input_dict.items() }
  
def get_user_id() -> str:
  """
  Returns a unique ID for the current user
  If the user is logged in, uses their user id, otherwise uses session id.
  """
  info = get_user_info()
  
  if info:
    return str(info["id"])
  else:
    return str(user_info().session)

def get_user_email() -> Optional[str]:
  """Returns the user's email, if it exists, or None"""
  info = get_user_info()

  if info:
    return info["email"]
  else:
    return None

def new_entry(name="", court_name="", court_emails=dict(), files=[]) -> str:
  """
  Creates a new upload entry in the database
  
  Args:
    name (str): the name of who is completing the form
    doc_name (str): the name of the document
    court_name (str): the name of the court to file
    file_path (str): the path of the assembled file (on disk)

  Returns (str):
    A unique ID corresponding to the current submission
  """
  if court_name not in court_emails:
    # in our system, this should never happen, but will leave in for debugging
    raise ValueError(f"Court {court_name} does not exist")

  connection = connect(**db_config)
  submission_id = None
  
  with connection.cursor() as cursor:
    # create a new interview submission
    cursor.execute("INSERT INTO interviews (timestamp, name, court_name, user_id) VALUES (%s, %s, %s, %s) RETURNING id", (datetime.now(), name, court_name, get_user_id()))
    submission_id = cursor.fetchone()[0]

    # save the file metadata (NOT the files themselves)
    for file in files:
      sensitive = defined("file.sensitive") and file.sensitive
      cursor.execute("INSERT INTO files (number, filename, mimetype, sensitive, submission_id) VALUES (%s, %s, %s, %s, %s)", (file.number, file.filename, file.mimetype, sensitive, submission_id))
    
  connection.commit()  
  connection.close()
  
  return str(submission_id)

def url_for_submission(id="") -> str:
  """Returns the url that one can use to view the submission (if logged in and allowed)"""
  return interview_url(i="docassemble.MAVirtualCourt:submission.yml", id=id)

def can_access_submission(submission_id="", emails_to_courts=dict()) -> bool:
  """
  Determines whether the current user can access the files related to the submission, submission_id
  If the user is authorized to access the files, we also grant the user access to view the files.

  Args:
    submission_id (str): the id of the submission we are interested in
    emails_to_courts (dict): a dictionary mapping court emails to names

  Returns (bool):
    True if the user made the initial submission, or the user is with the court that the submission was filed; otherwise, false
  """
  connection = connect(**db_config)
  
  with connection.cursor() as cursor:
    # get the submission, submission_id
    cursor.execute("SELECT court_name, user_id FROM interviews WHERE id = (%s)", (submission_id,))
    entry = cursor.fetchone()

    authorized = False

    if entry is None:
      authorized = False
    elif get_user_id() == str(entry[1]):
      authorized = True
    else:
      user_email = get_user_email()

      if user_email:
        authorized = entry[0] == emails_to_courts.get(user_email)

    if authorized:
      cursor.execute("SELECT number, filename, mimetype, sensitive FROM files WHERE submission_id = (%s)", (submission_id,))
      files = cursor.fetchall()

      # if the user is authorized, grant access to all the files
      for [number, filename, mimetype, _sensitive] in files:
        file = DAFile(number=number, filename=filename, mimetype=mimetype)
        file.user_access(get_user_id())

  connection.close()

  return authorized

def get_files(submission_id="") -> list:
  """
  Gets a list of files for the submission, submission_id and authorizes the current user access
  We assume that the user already has access to the files when calling this function.
  If the user does not have access, then docassemble will not show the files.

  Args:
    submission_id (str): the id of the submission to find

  Returns (List[DAFile]):
    a list of DAFiles corresponding to all the files that were created in this submission
  """
  connection = connect(**db_config)
  cursor = connection.cursor()

  cursor.execute("SELECT number, filename, mimetype, sensitive FROM files WHERE submission_id = (%s)", (submission_id,))
  entries = cursor.fetchall()

  if entries is None or len(entries) == 0:
    raise ValueError(f"Could not find a submission {submission_id}")

  files = []

  # recreate all the files from metadata
  for [number, filename, mimetype, _sensitive] in entries:
    files.append(DAFile(number=number, filename=filename, mimetype=mimetype))
    
  cursor.close()
  connection.close()

  return files

def get_accessible_submissions(emails_to_courts={}) -> Tuple[list, str]:
  """
  Gets a list of all the submissions (id, time, other data) that the current user is authorized to see

  If the user is a court, it shows the name of who submitted the form.
  Otherwise, it will show the court to which the form was sent.

  Args:
    emails_to_courts (dict): a dictionary mapping emails to court names

  Returns (Tuple[list,str]):
    a list of all the entries the user can view, and a title for the third field
  """
  connection = connect(**db_config)
  cursor = connection.cursor()

  court_name = None
  email = get_user_email()

  if email:
    court_name = emails_to_courts.get(email)

  if court_name:
    cursor.execute("SELECT id, timestamp, name FROM interviews WHERE court_name = (%s)", (court_name,))
    field_name = "Name"
  else:
    user_id = get_user_id()
    cursor.execute("SELECT id, timestamp, court_name FROM interviews WHERE user_id = (%s)", (user_id,))
    field_name = "Court name"

  results = [cursor.fetchall(), field_name]

  cursor.close()
  connection.close()

  return results


def send_attachments(name="", court_name="", court_emails=dict(), files=[], submission_id="") -> bool:
  """
  Sends one or nore non-sensitive applications and submission info to the email of the court, court_name

  The email includes the user's name, submission id, and a list of non-sensitive forms. 
  If there are any sensitive forms in the files list, they will not be sent. 
  Instead, the recipient will be instructed to access the submission on our own site.

  Args:
    name (str): the name of the submitter
    court_name (str): the name of the court that should be receiving this email
    court_emails (dict): a dictionary mapping court names to emails
    files (List[DAFile]): a list of DAFiles (possibly sensitive) to be sent
    submission_id (str): the unique id for this submission

  Raises:
    ValueError if court_name is not in the court_emails dict

  Returns (bool):
    True if the email was sent successfully, false otherwise
  """
  if court_name not in court_emails:
    # in our system, this should never happen, but will leave in for debugging
    raise ValueError(f"Court {court_name} does not exist")

  attachments = [file for file in files if not defined("file.sensitive") or not file.sensitive]
  court_email = court_emails[court_name]

  filenames = [file.filename for file in attachments]
  filenames_str = "\n    ".join(filenames)
  submission_url = url_for_submission(id=submission_id)

  if len(attachments) != len(files):
    if len(attachments) == 0:
      body = dedent(f"""
      Dear {court_name}:

      {name} has submitted {len(files)} file(s) online. However, these file(s) have sensitive information, and will not be sent over email.
      
      Please access these forms with the following submission id: {submission_url}.
      """)

      attachments = None
    else:
      body = dedent(f"""
      Dear {court_name}:
      
      You are receiving {quantity_noun(len(attachments), "file")} from {name}:
      {filenames_str}

      However, there are also {quantity_noun(len(files) - len(attachments), "form")} which are sensitive that will not be sent over email.

      Please access these forms with the following submission id: {submission_url}.
      """)
  else:
    body = dedent(f"""
    Dear {court_name}:

    You are receiving {quantity_noun(len(attachments), "file")} from {name}:
    {filenames_str}

    The reference ID for these forms is {submission_url}.
    """)

  return send_email(to=court_email, subject=f"Online form submission {submission_id}", body=body, attachments=attachments)