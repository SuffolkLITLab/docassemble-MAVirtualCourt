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
    if not hasattr(self, 'attorneys'):
      self.initializeAttribute('attorneys', PeopleList)
    if not hasattr(self, 'other_parties'):
      self.initializeAttribute('other_parties', PeopleList)

  # We use a property decorator because Docassemble expects this to be an attribute, not a method
  @property
  def complete_proceeding(self):
    """Tells docassemble the list item has been gathered when the variables named below are defined."""
    self.user_role
    self.case_status
    self.children.gathered
    self.other_parties.gather()
    # We're going to gather this per-attorney instead of
    # per-case now
    #if self.case_status == 'pending':
    #  self.attorneys.gather()

  def child_letters(self):
    """Return ABC if children lettered A,B,C are part of this case"""
    return ''.join([child.letter for child in self.children])

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
    if self.case_status in ['adoption',"adoption-pending", "adoption-closed"]:
      return 'Adoption'
    elif self.case_status == 'pending':
      return 'Pending'
    elif self.case_status == 'custody-closed':
      return "Custody awarded to " + self.person_given_custody + ", " + self.date_of_custody.format("yyyy-MM-dd")
    elif self.case_status == 'non-custody-closed':
      return self.what_happened
    else:
      return self.case_status

  def case_description(self):
    """Returns a short description of the other case or proceeding meant to display to identify it
    during list gathering in the course of the interview"""
    description = ""
    description += self.court_name
    if hasattr(self, 'docket_number') and len(self.docket_number.strip()):
      description += ', case number: ' + self.docket_number
    description += " (" + str(self.children) + ")"
    return description

  def __str__(self):
    return self.case_description()

class OtherProceedingList(DAList):
  """Represents a list of care and custody proceedings"""
  def init(self, *pargs, **kwargs):
    super(OtherProceedingList, self).init(*pargs, **kwargs)
    self.object_type = OtherProceeding
    self.complete_attribute = 'complete_proceeding' # triggers the complete_proceeding method of an OtherProceeding

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

def number_to_letter(n):
  """Returns a capital letter representing ordinal position. E.g., 1=A, 2=B, etc. Appends letters
  once you reach 26 in a way compatible with Excel/Google Sheets column naming conventions. 27=AA, 28=AB...
  """
  string = ""
  if n is None:
    n = 0
  while n > 0:
    n, remainder = divmod(n - 1, 26)
    string = chr(65 + remainder) + string
  return string

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
        define(map_names(field), '""') # set to an empty string 
        #define(map_names(field), 'DAEmpty()') # set to special Docassemble empty object. Should work in DA > 1.1.4
    # Handle special case of an address that we skipped filling in on the form
    elif map_names(field).endswith('address.on_one_line()'):
      address_obj_name = map_names(field).partition('.on_one_line')[0]
      if not defined(address_obj_name+'.address'): # here we're checking for an empty street address attribute
        # define(individual_name, '') # at this point this should be something like user.address
        try:
          exec(address_obj_name + "= DAEmpty()")
        except:
          pass
        # define(address_obj_name, DAEmpty()) 
    elif map_names(field).endswith('address.line_two()'):
      address_obj_name = map_names(field).partition('.line_two')[0]
      if not defined(address_obj_name+'.city'): # We check for an undefined city attribute
        try:
          exec(address_obj_name + "= DAEmpty()")
        except:
          pass
    elif map_names(field).endswith('address.block()'):
      address_obj_name = map_names(field).partition('.block')[0]
      if not defined(address_obj_name+'.address'): # We check for an undefined street address
        try:
          exec(address_obj_name + "= DAEmpty()")
        except:
          pass


def filter_letters(letter_strings):
  """Used to take a list of letters like ["A","ABC","AB"] and filter out any duplicate letters."""
  # There is probably a cute one liner, but this is easy to follow and
  # probably same speed
  unique_letters = set()
  for string in letter_strings:
    for letter in string:
      unique_letters.add(letter)
  return ''.join(sorted(unique_letters))