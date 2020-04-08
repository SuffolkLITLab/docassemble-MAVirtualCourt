from docassemble.base.functions import define, defined, value

from docassemble.base.util import Address, Individual, DAEmpty, DAList, Thing, DAObject
from docassemble.assemblylinewizard.interview_generator import map_names

class PeopleList(DAList):
    def init(self, *pargs, **kwargs):
        super(PeopleList, self).init(*pargs, **kwargs)
        self.object_type = Individual

class VCCase(Thing):
  # add a complete attribute
  # add a .tostring method which spits out description  
  def __str__(self):
    return self.description

def trigger_user_questions(interview_metadata_dict, question_order = None):
  """There may be a more elegant way to handle this."""
  if not question_order:
    question_order = [
      'guardian',
      'caregiver',
      'guardian_ad_litem',
      'attorney',
      'translator',
      'witness',
      'spouse',
      'user',
      'user.address',
      'user.email',
    ]
  for field in question_order:
    if field in interview_metadata_dict.get('built_in_fields_used',[]):
      if isinstance(value(field),Individual):
        value(field + '.name.first')
      elif isinstance(value(field),Address):
        value(field + '.address')      
      else:
        value(field)

def trigger_court_questions(interview_metadata_dict, question_order = None):
  """ Not sure if we need this function yet."""
  # if not question_order:
  #   question_order = [
  #     'court.name',
  #     'docket_number[0]'
  #   ]

  # for field in question_order:
  #   if map_names(field) in interview_metadata_dict.get('',[]):
  #     value(field)  

def trigger_signature_flow(interview_metadata_dict, question_order = None):
  if not question_order:
    question_order = [

    ]

def mark_unfilled_fields_empty(interview_metadata_dict):
  """Given an interview metadata dictionary, transform any un-filled fields into DAEmpty()"""
  for field_dict in interview_metadata_dict.get('field_list',[]) + interview_metadata_dict.get('built_in_fields_used',[]):
    try:
        field = field_dict['variable'] # Our list of fields is a dictionary
    except:
        continue
    # Make sure we don't try to define a method
    # Also, don't set any signatures to DAEmpty
    if not map_names(field).endswith('.signature') and not '(' in map_names(field):
      if not defined(map_names(field)):
        define(map_names(field), '') # set to special Docassemble empty object
        #define(map_names(field), DAEmpty()) # set to special Docassemble empty object
    # Handle special case of an address that we skipped filling in on the form
    elif map_names(field).endswith('address.on_one_line()'):
      individual_name = map_names(field).partition('.on_one_line')[0]
      if not defined(individual_name+'.address'): # here we're checking for an empty street address attribute
        define(individual_name, '') # at this point this should be something like user.address
    elif map_names(field).endswith('address.line_two()'):
      individual_name = map_names(field).partition('.line_two')[0]
      if not defined(individual_name+'.city'):
        define(individual_name, '')

