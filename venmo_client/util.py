import datetime

from typing import Union

__all__ = [
    'canonicalize_date'
]

def canonicalize_date(
    date_or_str: Union[str, datetime.date]) -> datetime.date:
  if isinstance(date_or_str, datetime.date):
    return date_or_str
  return datetime.datetime.strptime(date_or_str, '%Y-%m-%d').date()
