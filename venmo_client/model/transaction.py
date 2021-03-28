import dataclasses
import datetime

from typing import Any, Dict, List, Optional

from venmo_client.model import user


@dataclasses.dataclass(frozen=True)
class Target:
  merchant: Optional[str]
  redeemable_target: Optional[str]
  phone: Optional[str]
  user: user.User
  type: str
  email: Optional[str]

  @classmethod
  def new(cls, **data):
    data = dict(data,
        user=user.User.new(**data['user']))
    return Target(**data)


@dataclasses.dataclass(frozen=True)
class Payment:
  status: str
  id: str
  date_authorized: Optional[datetime.datetime]
  merchant_split_purchase: Optional[bool]
  date_completed: datetime.datetime
  target: Target
  audience: str
  actor: user.User
  note: str
  amount: float
  action: str
  date_created: datetime.datetime
  date_reminded: Optional[datetime.datetime]
  external_wallet_payment_info: Optional[str]

  @classmethod
  def new(cls, **data):
    data = dict(data,
        actor=user.User.new(**data['actor']),
        target=Target.new(**data['target']),
        date_authorized=datetime.datetime.fromisoformat(
          data['date_authorized']) if data['date_authorized'] else None,
        date_created=datetime.datetime.fromisoformat(data['date_created']),
        date_completed=datetime.datetime.fromisoformat(data['date_completed']),
        date_reminded=datetime.datetime.fromisoformat(
          data['date_reminded']) if data['date_reminded'] else None,
        )
    return cls(**data)


@dataclasses.dataclass(frozen=True)
class Transaction:
  date_updated: datetime.datetime
  transfer: Optional[bool]
  app: Dict[str, Any]
  comments: List[Any]
  payment: Payment
  note: str
  audience: str
  likes: List[Any]
  mentions: List[Any]
  date_created: datetime.datetime
  type: str
  id: str
  authorization: Optional[str]
  transaction_external_id: Optional[str] = None

  @classmethod
  def new(cls, *, date_updated, date_created, payment, **data):
    date_updated = datetime.datetime.fromisoformat(date_updated)
    date_created = datetime.datetime.fromisoformat(date_created)
    if payment:
      payment = Payment.new(**payment)
    return cls(date_updated=date_updated, date_created=date_created,
        payment=payment, **data)
