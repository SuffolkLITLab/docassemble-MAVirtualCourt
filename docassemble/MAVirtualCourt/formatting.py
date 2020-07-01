def thousands(num:float) -> str:
  """
  Return a whole number formatted with thousands separator.
  """
  try:
    return f"{int(num):,}"
  except:
    return num