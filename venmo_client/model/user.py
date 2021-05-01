import dataclasses
import datetime

from typing import Any, Dict, List, Optional


@dataclasses.dataclass(frozen=True)
class User:
  username: str
  last_name: str
  friends_count: Optional[int]
  is_group: bool
  is_active: bool
  trust_request: Optional[bool]
  phone: Optional[str]
  profile_picture_url: str
  is_blocked: bool
  id: str
  identity: Optional[str]
  date_joined: datetime.datetime
  about: str
  display_name: str
  first_name: str
  friend_status: str
  email: str
  is_payable: bool
  identity_type: str
  is_venmo_team: bool = False

  @classmethod
  def new(cls, **data: Dict[str, Any]) -> 'User':
    data = dict(
        data,
        date_joined=datetime.datetime.fromisoformat(data['date_joined']))
    return cls(**data)
