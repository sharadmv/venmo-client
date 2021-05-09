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

  def serialize(self):
    return dict(
        username=self.username,
        last_name=self.last_name,
        friends_count=self.friends_count,
        is_group=self.is_group,
        is_active=self.is_active,
        trust_request=self.trust_request,
        phone=self.phone,
        profile_picture_url=self.profile_picture_url,
        is_blocked=self.is_blocked,
        id=self.id,
        identity=self.identity,
        date_joined=self.date_joined.isoformat(),
        about=self.about,
        display_name=self.display_name,
        first_name=self.first_name,
        friend_status=self.friend_status,
        email=self.email,
        is_payable=self.is_payable,
        identity_type=self.identity_type,
        is_venmo_team=self.is_venmo_team)


@dataclasses.dataclass(frozen=True)
class Merchant:
  braintree_merchant_id: str
  datetime_updated: datetime.datetime
  display_name: str
  image_datetime_updated: datetime.datetime
  is_subscription: bool
  image_url: str
  paypal_merchant_id: str
  id: str
  datetime_created: datetime.datetime

  @classmethod
  def new(cls, braintree_merchant_id, datetime_updated, display_name,
      image_datetime_updated, is_subscription, image_url, paypal_merchant_id,
      id, datetime_created) -> 'Merchant':
    datetime_updated = datetime.datetime.fromisoformat(datetime_updated)
    image_datetime_updated = datetime.datetime.fromisoformat(image_datetime_updated)
    datetime_created = datetime.datetime.fromisoformat(datetime_created)
    return cls(braintree_merchant_id, datetime_updated, display_name,
        image_datetime_updated, is_subscription, image_url, paypal_merchant_id,
        id, datetime_created)

  def serialize(self):
    return dict(
        braintree_merchant_id=self.braintree_merchant_id,
        datetime_updated=self.datetime_updated.isoformat(),
        display_name=self.display_name,
        image_datetime_updated=self.image_datetime_updated.isoformat(),
        is_subscription=self.is_subscription,
        image_url=self.image_url,
        paypal_merchant_id=self.paypal_merchant_id,
        id=self.id,
        datetime_created=self.datetime_created.isoformat())
