from docassemble.base.functions import define, defined, value

from docassemble.base.util import Address, Individual, DAEmpty, DAList, Thing, DAObject
from docassemble.assemblylinewizard.interview_generator import map_names

class AddressList(DAList):
  """Store a list of Address objects"""
  def init(self, *pargs, **kwargs):
    super(AddressList, self).init(*pargs, **kwargs)
    self.object_type = Address

class PeopleList(DAList):
  """Used to represent a list of people. E.g., defendants, plaintiffs, children"""
  def init(self, *pargs, **kwargs):
    super(PeopleList, self).init(*pargs, **kwargs)
    self.object_type = VCIndividual

class VCIndividual(Individual):
  """Used to represent an Individual on the assembly line/virtual court project.
  Two custom attributes are objects and so we need to initialize: `previous_addresses` 
  and `other_addresses`
  """
  def init(self, *pargs, **kwargs):
    super(VCIndividual, self).init(*pargs, **kwargs)
    # Initialize the attributes that are themselves objects. Requirement to work with Docassemble
    # See: https://docassemble.org/docs/objects.html#ownclassattributes
    if not hasattr(self, 'previous_addresses'):
      self.initializeAttribute('previous_addresses', AddressList)
    if not hasattr(self, 'other_addresses'):
      self.initializeAttribute('other_addresses', AddressList)      

class OtherProceeding(DAObject):
  """Currently used to represents a care and custody proceeding."""
  def init(self, *pargs, **kwargs):
    super(OtherProceeding, self).init(*pargs, **kwargs)
    if not hasattr(self, 'children'):
      self.initializeAttribute('children', PeopleList)
    self.complete_attribute = 'complete_proceeding'    

  @property
  def complete_proceeding(self):
    self.role
    self.case_status
    self.children.gathered

  def status(self):
    """Should return the status of the case, suitable to fit on Section 7 of the affidavit disclosing care or custody"""
    # I think there's four possible ways the status could go
    # -if the case is an adoption: status should say "adoption"
    # -if the case is still pending: status should say "pending"
    # -if the case is closed and was about custody: should should say "custody to [person], [date of custody award]"
    # -if the case is closed and was about something other than custody, I would do a very brief outcome of the case and the date the case closed, like "Father to pay child support, [date of judgment]"    
    # - Adoption (pending or closed): adoption
    # - Non-adoption case without a final decision yet: pending
    # - Custody case that is complete: custody-closed
    # - Non-custody case that is complete: non-custody-closed
    if self.case_status == 'adoption':
      return 'Adoption'
    elif self.case_status == 'pending':
      return 'Pending'
    elif self.case_status == 'custody-closed':
      return "Custody awarded to " + self.person_given_custody + ", " + self.date_of_custody.format("yyyy-MM-dd")
    elif self.case_status == 'non-custody-closed':
      return self.what_happened
    else:
      return self.case_status

  def __str__(self):
    return self.status()

class OtherProceedingList(DAList):
  """Represents a list of care and custody proceedings"""
  def init(self, *pargs, **kwargs):
    super(OtherProceedingList, self).init(*pargs, **kwargs)
    self.object_type = OtherProceeding
  def includes_adoption(self):
    """Returns true if any of the listed proceedings was an adoption proceeding."""
    for case in self.elements:
      if case.case_status == 'adoption':
        return True

def get_signature_fields(interview_metadata_dict):
  """Returns a list of the signature fields in the list of fields, based on assembly line naming conventions"""
  signature_fields = []
  for field_dict in (interview_metadata_dict.get('built_in_fields_used',[]) + interview_metadata_dict.get('fields',[])):
    field = map_names(field_dict.get('variable',''))
    if field.endswith('.signature'):
      signature_fields.append(field)
  return signature_fields

# Below commented out functions were replaced by code blocks in basic-questions.yml
# def trigger_user_questions(interview_metadata_dict, question_order = None):
#   """There may be a more elegant way to handle this."""
#   if not question_order:
#     question_order = [
#       'guardian',
#       'caregiver',
#       'guardian_ad_litem',
#       'attorney',
#       'translator',
#       'witness',
#       'spouse',
#       'user',
#       'user.address',
#       'user.email',
#     ]
#   for field in question_order:
#     if field in interview_metadata_dict.get('built_in_fields_used',[]):
#       if isinstance(value(field),Individual):
#         value(field + '.name.first')
#       elif isinstance(value(field),Address):
#         value(field + '.address')      
#       else:
#         value(field)

# def trigger_court_questions(interview_metadata_dict, question_order = None):
#   """ Not sure if we need this function yet."""
#   # if not question_order:
#   #   question_order = [
#   #     'court.name',
#   #     'docket_number[0]'
#   #   ]

#   # for field in question_order:
#   #   if map_names(field) in interview_metadata_dict.get('',[]):
#   #     value(field)  

# def trigger_signature_flow(interview_metadata_dict, question_order = None):
#   if not question_order:
#     question_order = [

#     ]

def mark_unfilled_fields_empty(interview_metadata_dict):
  """Sets the listed fields that are not yet defined to an empty string. Requires an interview metadata dictionary
  as input parameter. Aid for filling in a PDF. This will not set ALL fields in the interview empty;
  only ones mentiond in the specific metadata dict."""
  # There are two dictionaries in the interview-specific metadata that list fields
  # fields and built_in_fields used. Some older interviews may use `field_list`
  # We loop over each field and check if it's already defined in the Docassemble interview's namespace
  # If it isn't, we set it to an empty string.
  for field_dict in interview_metadata_dict['field_list'] + interview_metadata_dict['built_in_fields_used'] + interview_metadata_dict['fields']:
    try:
        field = field_dict['variable'] # Our list of fields is a dictionary
    except:
        continue
    # Make sure we don't try to define a method
    # Also, don't set any signatures to DAEmpty
    # This will not work on a method call, other than the 3 we explicitly handle: 
    # address.line_two(), address.on_one_line(), and address.block()
    if not map_names(field).endswith('.signature') and not '(' in map_names(field):
      if not defined(map_names(field)):
        # define(map_names(field), '') # set to an empty string
        define(map_names(field), DAEmpty()) # set to special Docassemble empty object. Should work in DA > 1.1.4
    # Handle special case of an address that we skipped filling in on the form
    elif map_names(field).endswith('address.on_one_line()'):
      address_obj_name = map_names(field).partition('.on_one_line')[0]
      if not defined(address_obj_name+'.address'): # here we're checking for an empty street address attribute
        # define(individual_name, '') # at this point this should be something like user.address
        define(address_obj_name, DAEmpty()) 
    elif map_names(field).endswith('address.line_two()'):
      address_obj_name = map_names(field).partition('.line_two')[0]
      if not defined(address_obj_name+'.city'): # We check for an undefined city attribute
        define(address_obj_name, DAEmpty())
    elif map_names(field).endswith('address.block()'):
      address_obj_name = map_names(field).partition('.block')[0]
      if not defined(address_obj_name+'.address'): # We check for an undefined street address
        define(address_obj_name, DAEmpty())


