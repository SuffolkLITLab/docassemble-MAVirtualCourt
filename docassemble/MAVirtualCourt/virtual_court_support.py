from docassemble.base.functions import define, defined, value, comma_and_list, word, comma_list, DANav, url_action, showifdef

from docassemble.base.util import Address, Individual, DAEmpty, DAList, Thing, DAObject, Person, date_difference
from docassemble.assemblylinewizard.interview_generator import map_names
import re

class AddressList(DAList):
  """Store a list of Address objects"""
  def init(self, *pargs, **kwargs):
    super(AddressList, self).init(*pargs, **kwargs)
    self.object_type = Address

  def __str__(self):
    return comma_and_list([item.on_one_line() for item in self])

class VCBusiness(Person):
  """A legal entity, like a school, that is not an individual. Has a .name.text attribute that must be defined to reduce to text."""
  pass

class VCBusinessList(DAList):
  """Store a list of VCBusinesses. Includes method .names_and_addresses_on_one_line to reduce to a semicolon-separated list"""
  def init(self, *pargs, **kwargs):
    super(VCBusinessList, self).init(*pargs, **kwargs)
    self.object_type = VCBusiness

  def names_and_addresses_on_one_line(self, comma_string='; '):
    """Returns the name of each business followed by their address, separated by a semicolon"""
    return comma_and_list( [str(person) + ", " + person.address.on_one_line() for person in self], comma_string=comma_string)

class PeopleList(DAList):
  """Used to represent a list of people. E.g., defendants, plaintiffs, children"""
  def init(self, *pargs, **kwargs):
    super(PeopleList, self).init(*pargs, **kwargs)
    self.object_type = VCIndividual

  def names_and_addresses_on_one_line(self, comma_string='; '):
    """Returns the name of each person followed by their address, separated by a semicolon"""
    return comma_and_list([str(person) + ', ' + person.address.on_one_line() for person in self], comma_string=comma_string)

  def familiar(self):
    return comma_and_list([person.name.familiar() for person in self])

  def familiar_or(self):
    return comma_and_list([person.name.familiar() for person in self],and_string=word("or"))

class UniquePeopleList(PeopleList):
  pass

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

  def phone_numbers(self):
    nums = []
    if hasattr(self, 'mobile_number') and self.mobile_number:
      nums.append(self.mobile_number + ' (cell)')
    if hasattr(self, 'phone_number') and self.phone_number:
      nums.append(self.phone_number + ' (other)')
    return comma_list(nums)
  
  def merge_letters(self, new_letters):
    """If the Individual has a child_letters attribute, add the new letters to the existing list"""
    if hasattr(self, 'child_letters'):
      self.child_letters = filter_letters([new_letters, self.child_letters])
    else:
      self.child_letters = filter_letters(new_letters)

  def formatted_age(self):
    dd = date_difference(self.birthdate)
    if dd.years >= 2:
      return '%d years' % (int(dd.years),)
    if dd.weeks > 12:
      return '%d months' % (int(dd.years * 12.0),)
    if dd.weeks > 2:
      return '%d weeks' % (int(dd.weeks),)
    return '%d days' % (int(dd.days),)

# TODO: create a class for OtherCases we list on page 1. Is this related
# to the other care/custody proceedings?
class OtherCase(Thing):
  pass

class OtherProceeding(DAObject):
  """Currently used to represents a care and custody proceeding."""
  def init(self, *pargs, **kwargs):
    super(OtherProceeding, self).init(*pargs, **kwargs)
    if not hasattr(self, 'children'):
      self.initializeAttribute('children', PeopleList)
    if not hasattr(self, 'attorneys'):
      self.initializeAttribute('attorneys', PeopleList)
    if not hasattr(self, 'attorneys_for_children'):
      self.initializeAttribute('attorneys_for_children', PeopleList)
    if not hasattr(self, 'other_parties'):
      self.initializeAttribute('other_parties', PeopleList)
    if not hasattr(self, 'gals'):
      self.initializeAttribute('gals', GALList.using(ask_number=True))

  # We use a property decorator because Docassemble expects this to be an attribute, not a method
  @property
  def complete_proceeding(self):
    """Tells docassemble the list item has been gathered when the variables named below are defined."""
    # self.user_role # Not asked for adoption cases
    self.case_status
    self.children.gathered
    self.other_parties.gather()
    if self.is_open:
      self.atty_for_user
      if self.atty_for_children:
        if len(self.children) > 1:
          self.attorneys_for_children.gather()
      if self.has_gal:
        self.gals.gather()
      else:
        self.gals.auto_gather=True
        self.gals.gathered=True
    return True
    # We're going to gather this per-attorney instead of
    # per-case now
    #if self.case_status == 'pending':
    #  self.attorneys.gather()

  def child_letters(self):
    """Return ABC if children lettered A,B,C are part of this case"""
    return ''.join([child.letter for child in self.children if child.letter])

  def status(self):
    """Should return the status of the case, suitable to fit on Section 7 of the affidavit disclosing care or custody"""
    if self.case_status in ['adoption',"adoption-pending", "adoption-closed"]:
      return 'Adoption'
    elif hasattr(self, 'custody_awarded') and self.custody_awarded:
      return "Custody awarded to " + self.person_given_custody + ", " + self.date_of_custody.format("yyyy-MM-dd")
    elif not self.is_open:
      return "Closed"
    elif self.is_open:
      return 'Pending'
    else:
      return self.case_status.title()

  def role(self):
    """Return the letter representing user's role in the case. If it's an adoption case, don't return a role."""
    if self.case_status == 'adoption':
      return ''
    return self.user_role

  def case_description(self):
    """Returns a short description of the other case or proceeding meant to display to identify it
    during list gathering in the course of the interview"""
    description = ""
    description += self.case_status.title() + " case in "
    description += self.court_name
    if hasattr(self, 'docket_number') and len(self.docket_number.strip()):
      description += ', case number: ' + self.docket_number
    description += " (" + str(self.children) + ")"
    return description

  def role(self):
    """Return the letter representing user's role in the case. If it's an adoption case, don't return a role."""
    if self.case_status == 'adoption':
      return ''
    return self.user_role

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
  
  def get_gals(self, intrinsic_name):
    GALs = GALList(intrinsic_name, auto_gather=False,gathered=True)
    for case in self:
      if case.is_open and case.has_gal:
        for gal in case.gals:
          if gal.represented_all_children:
            gal.represented_children = case.children
          GALs.append(gal, set_instance_name=True)         
    return GALs

class GAL(VCIndividual):
  """This object has a helper for printing itself in PDF, as well as a way to merge attributes for duplicates"""
  def status(self):
    return str(self) + ' (' + comma_and_list(self.represented_children) + ')'
  
  def is_match(self, new_gal):
    return str(self) == str(new_gal)

  def merge(self, new_gal):
    self.represented_children = PeopleList(elements=self.represented_children.union(new_gal.represented_children))

class GALList(PeopleList):
  """For storing a list of Guardians ad Litem in Affidavit of Care and Custody"""
  def init(self, *pargs, **kwargs):
    super(GALList, self).init(*pargs, **kwargs)
    self.object_type = GAL

  def append(self, new_item, set_instance_name=False):
    """Only append if this GAL has a unique name"""
    match = False
    for item in self:
      if item.is_match(new_item):
        match = True
        # Merge list of children represented if same name
        item.merge(new_item)
    if not match:
      return super().append(new_item, set_instance_name=set_instance_name)    
    return None

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
    # Empty strings will break this
    if field and not map_names(field).endswith('.signature') and not '(' in map_names(field):
      if not defined(map_names(field)):
        define(map_names(field), '') # set to an empty string 
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
  if isinstance(letter_strings, str):
    letter_strings = [letter_strings]
  for string in letter_strings:
    if string: # Catch possible None values
      for letter in string:
        unique_letters.add(letter)
  try:
    retval = ''.join(sorted(unique_letters))
  except:
    reval = ''
  return retval

def yes_no_unknown(var_name, condition, unknown="Unknown", placeholder=0):
  """Return 'unknown' if the value is None rather than False. Helper for PDF filling with
  yesnomaybe fields"""
  if condition:
    return value(var_name)
  elif condition is None:
    return unknown
  else:
    return placeholder

def section_links(nav):
  """Returns a list of clickable navigation links without animation."""
  sections = nav.get_sections()
  section_link = []
  for section in sections:
    for key in section:
      section_link.append('[' + section[key] + '](' + url_action(key) + ')' )

  return section_link    

def space(var_name, prefix=' ', suffix=''):
  """If the value as a string is defined, return it prefixed/suffixed. Defaults to prefix
  of a space. Helps build a sentence with less cruft. Equivalent to SPACE function in
  HotDocs."""
  if var_name and isinstance(var_name, str) and re.search(r'[A-Za-z][A-Za-z0-9\_]*', var_name) and defined(var_name) and value(var_name):
    return prefix + showifdef(var_name) + suffix
  else:
    return ''