import re

"""This is ripping off a bandaid: the MAVirtualCourt has depended on the `map_names` function
from the assemblylinewizard (aka the Weaver) for a while. However, this now dependency from the
now deprecated MAVirtualCourt library makes it more difficult to refactor and improve the Weaver.

This code is from the https://github.com/SuffolkLITLab/docassemble-assemblylinewizard/commit/d403d8b8f37e5e8ea3ad48ba15a5e0214be9b465 commit of the Weaver, copied over, so it can be refactored
in the weaver.
"""


# This is to workaround fact you can't do local import in Docassemble playground
class Object(object):
  pass

generator_constants = Object()

# Words that are reserved exactly as they are
generator_constants.RESERVED_WHOLE_WORDS = [
  'signature_date',
  'docket_number',
  'user_needs_interpreter',
  'user_preferred_language',
]

# Prefixes for singular person-like objects, like trial courts that
# should be left undefined to trigger their question
generator_constants.UNDEFINED_PERSON_PREFIXES = [
  "trial_court",
]

# Prefixes as they would appear in a PDF (singular)
generator_constants.RESERVED_PREFIXES = ["user",
  "other_party",
  "child",
  "plaintiff",
  "defendant",
  "petitioner",
  "respondent",
  "spouse",
  "parent",
  "caregiver",
  "attorney",
  "translator",
  "debt_collector",
  "creditor",
  "witness",
  "court",
  "signature_date",
  # Can't find a way to make order not matter here
  # without making everything in general more messy
  "guardian_ad_litem",
  "guardian",
  "decedent",
  "interested_party",
  "trial_court",
  "docket_numbers",
  ]

generator_constants.RESERVED_PERSON_PLURALIZERS_MAP = {
  'user': 'users',
  'plaintiff': 'plaintiffs',
  'defendant': 'defendants',
  'petitioner': 'petitioners',
  'respondent': 'respondents',
  'spouse': 'spouses',
  'parent': 'parents',
  'guardian': 'guardians',
  'caregiver': 'caregivers',
  'attorney': 'attorneys',
  'translator': 'translators',
  'debt_collector': 'debt_collectors',
  'creditor': 'creditors',
  # Non "s" plurals
  'other_party': 'other_parties',
  'child': 'children',
  'guardian_ad_litem': 'guardians_ad_litem',
  'witness': 'witnesses',
  'decedent': 'decedents',
  'interested_party': 'interested_parties',
}

generator_constants.RESERVED_PLURALIZERS_MAP = {** generator_constants.RESERVED_PERSON_PLURALIZERS_MAP, **{
  'court': 'courts', # for backwards compatibility
  'docket_numbers': 'docket_numbers',  
}}

# Any reason to not make all suffixes available to everyone?
# Yes: it can break variables that overlap but have a different meaning
# Better to be explicit

# Some common attributes that can be a clue it's a person object
generator_constants.PEOPLE_SUFFIXES_MAP = {
  '_name': "",  # full name
  '_name_full': "",  # full name
  '_name_first': ".name.first",
  '_name_middle': ".name.middle",
  '_name_middle_initial': ".name.middle_initial()",
  '_name_last': ".name.last",
  '_name_suffix': ".name.suffix",
  '_gender': ".gender",
  # '_gender_male': ".gender == 'male'",
  # '_gender_female': ".gender == 'female'",
  '_birthdate': ".birthdate.format()",
  '_age': ".age_in_years()",
  '_email': ".email",
  '_phone': ".phone_number",
  '_phone_number': ".phone_number",
  '_mobile': ".mobile_number",
  '_mobile_number': ".mobile_number",
  '_phones': ".phone_numbers()",
  '_address_block': ".address.block()",
  # TODO: deprecate street and street2 from existing forms and documentation
  '_address_street': ".address.address",
  '_address_street2': ".address.unit",
  '_address_address': ".address.address",
  '_address_unit': ".address.unit",
  '_address_city': ".address.city",
  '_address_state': ".address.state",
  '_address_zip': ".address.zip",
  '_address_county': ".address.county",
  '_address_country': ".address.country",
  '_address_on_one_line': ".address.on_one_line()",
  '_address_line_one': ".address.line_one()",
  '_address_city_state_zip': ".address.line_two()",
  '_signature': ".signature",
  '_mailing_address_block': ".mailing_address.block()",
  '_mailing_address_street': ".mailing_address.address",
  '_mailing_address_street2': ".mailing_address.unit",
  '_mailing_address_address': ".mailing_address.address",
  '_mailing_address_unit': ".mailing_address.unit",
  '_mailing_address_city': ".mailing_address.city",
  '_mailing_address_state': ".mailing_address.state",
  '_mailing_address_zip': ".mailing_address.zip",
  '_mailing_address_county': ".mailing_address.county",
  '_mailing_address_country': ".mailing_address.country",
  '_mailing_address_on_one_line': ".mailing_address.on_one_line()",
  '_mailing_address_line_one': ".mailing_address.line_one()",
  '_mailing_address_city_state_zip': ".mailing_address.line_two()",
  '_mailing_address': ".mailing_address",
}

# reserved_suffixes_map
generator_constants.RESERVED_SUFFIXES_MAP = {**generator_constants.PEOPLE_SUFFIXES_MAP, **{
  # Court-specific
  # '_name_short': not implemented,
  '_division': ".division",
  '_county': ".address.county",
  '_department': ".department",
}}


spaces = re.compile(r'[ \n]+')
invalid_var_characters = re.compile(r'[^A-Za-z0-9_]+')
digit_start = re.compile(r'^[0-9]+')

def remove_multiple_appearance_indicator(label: str) -> str:
    return re.sub(r'_{2,}\d+', '', label)


def get_reserved_label_parts(prefixes:list, label:str):
  """
  Return an re.matches object for all matching variable names,
  like user1_something, etc.
  """
  return re.search(r"^(" + "|".join(prefixes) + ')(\d*)(.*)', label)


def varname(var_name:str)->str:
    if var_name:
      var_name = var_name.strip() 
      var_name = spaces.sub(r'_', var_name)
      var_name = invalid_var_characters.sub(r'', var_name)
      var_name = digit_start.sub(r'', var_name)
      return var_name
    return var_name


def map_names(label, document_type="pdf", reserved_whole_words=generator_constants.RESERVED_WHOLE_WORDS,
              custom_people_plurals_map=None, 
              reserved_prefixes=generator_constants.RESERVED_PREFIXES,
              undefined_person_prefixes=generator_constants.UNDEFINED_PERSON_PREFIXES,
              reserved_pluralizers_map = generator_constants.RESERVED_PLURALIZERS_MAP,
              reserved_suffixes_map=generator_constants.RESERVED_SUFFIXES_MAP):
  """For a given set of specific cases, transform a
  PDF field name into a standardized object name
  that will be the value for the attachment field."""
  if document_type.lower() == "docx":
    return label # don't transform DOCX variables

  if custom_people_plurals_map is None:
    custom_people_plurals_map = {}

  # Turn spaces into `_`, strip non identifier characters
  label = varname(label)

  # Remove multiple appearance indicator, e.g. '__4' of 'users__4'
  label = remove_multiple_appearance_indicator(label)

  if (label in reserved_whole_words
   or label in reserved_pluralizers_map.values() 
   or label in undefined_person_prefixes
   or label in custom_people_plurals_map.values()):
     return label

  # Break up label into its parts: prefix, digit, the rest
  all_prefixes = reserved_prefixes + list(custom_people_plurals_map.values())
  label_groups = get_reserved_label_parts(all_prefixes, label)

  # If no matches to automateable labels were found,
  # just use the label as it is
  if label_groups is None or label_groups[1] == '':
    return label

  prefix = label_groups[1]
  # Map prefix to an adjusted version
  # At the moment, turn any singulars into plurals if needed, e.g. 'user' into 'users'
  adjusted_prefix = reserved_pluralizers_map.get(prefix, prefix)
  adjusted_prefix = custom_people_plurals_map.get(prefix, adjusted_prefix)
  # With reserved plurals, we're always using an index
  # of the plural version of the prefix of the label
  if (adjusted_prefix in reserved_pluralizers_map.values()
      or adjusted_prefix in custom_people_plurals_map.values()):
    digit = label_groups[2]
    if digit == '':
      index = '[0]'
    else:
      index = '[' + str(int(digit)-1) + ']'
  else:
    digit = ''
    index = ''
  
  # it's just a standalone, like "defendant", or it's a numbered singular
  # prefix, e.g. user3
  if label == prefix or label == prefix + digit:
    return adjusted_prefix + index # Return the pluralized standalone variable

  suffix = label_groups[3]
  # Avoid transforming arbitrary suffixes into attributes
  if not suffix in reserved_suffixes_map:
    return label  # return it as is

  # Get the mapped suffix attribute if present, else just use the same suffix
  suffix_as_attribute = reserved_suffixes_map.get(suffix, suffix)
  return "".join([adjusted_prefix, index, suffix_as_attribute])
