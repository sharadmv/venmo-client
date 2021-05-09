import dataclasses
import datetime

from typing import Any, Dict, List, Literal, Optional

from venmo_client.model import user as user_lib

@dataclasses.dataclass(frozen=True)
class FundingSource:
  transfer_to_estimate: datetime.datetime
  is_default: bool
  last_four: str
  account_status: str
  id: str
  bank_account: Optional[str]
  assets: Dict[str, Any]
  asset_name: str
  name: str
  image_url: Dict[str, Any]
  card: Optional[None]
  type: str
  
  @classmethod
  def new(cls, transfer_to_estimate=None, **data):
    transfer_to_estimate = (transfer_to_estimate and
        datetime.datetime.fromisoformat(transfer_to_estimate))
    return cls(transfer_to_estimate, **data)

  def serialize(self):
    return dict(
        transfer_to_estimate=self.transfer_to_estimate.isoformat(),
        is_default=self.is_default,
        last_four=self.last_four,
        account_status=self.account_status,
        id=self.id,
        bank_account=self.bank_account,
        assets=self.assets,
        asset_name=self.asset_name,
        name=self.name,
        image_url=self.image_url,
        card=self.card,
        type=self.type)


@dataclasses.dataclass(frozen=True)
class PaymentMethod:
  top_up_role: str
  default_transfer_destination: str
  fee: Optional[str]
  last_four: str
  id: str
  card: Optional[str]
  assets: Dict[str, Any]
  peer_payment_role: str
  name: str
  image_url: str
  bank_account: Dict[str, Any]
  merchant_payment_role: str
  type: str
  
  @classmethod
  def new(cls, **data):
    return cls(**data)

  def serialize(self):
    return dict(
        top_up_role=self.top_up_role,
        default_transfer_destination=self.default_transfer_destination,
        fee=self.fee,
        last_four=self.last_four,
        id=self.id,
        card=self.card,
        assets=self.assets,
        peer_payment_role=self.peer_payment_role,
        name=self.name,
        image_url=self.image_url,
        bank_account=self.bank_account,
        merchant_payment_role=self.merchant_payment_role,
        type=self.type)


@dataclasses.dataclass(frozen=True)
class Target:
  type: str
  phone: Optional[str]
  email: Optional[str]
  redeemable_target: Optional[str]
  user: Optional[user_lib.User] = None
  merchant: Optional[user_lib.Merchant] = None

  @classmethod
  def new(cls, *, type, phone, email, redeemable_target, **kwargs):
    target_kwargs = {}
    if type == 'user':
      target_kwargs['user'] = user_lib.User.new(**kwargs['user'])
    elif type == 'merchant':
      target_kwargs['merchant'] = user_lib.Merchant.new(**kwargs['merchant'])
    else:
      raise NotImplementedError(f'Unknown target type: {type}')
    return cls(type, phone, email, redeemable_target, **target_kwargs)

  def serialize(self):
    return dict(type=self.type, phone=self.phone, email=self.email,
        redeemable_target=self.redeemable_target,
        user=self.user and self.user.serialize(),
        merchant=self.merchant and self.merchant.serialize())

@dataclasses.dataclass(frozen=True)
class Payment:
  status: str
  id: str
  date_authorized: Optional[datetime.datetime]
  date_completed: datetime.datetime
  target: Target
  audience: str
  actor: user_lib.User
  note: str
  amount: float
  action: str
  date_created: datetime.datetime
  date_reminded: Optional[datetime.datetime]
  external_wallet_payment_info: Optional[str]

  @classmethod
  def new(cls, **data):
    data = dict(data,
        actor=user_lib.User.new(**data['actor']),
        target=Target.new(**data['target']),
        date_authorized=datetime.datetime.fromisoformat(
          data['date_authorized']) if data['date_authorized'] else None,
        date_created=datetime.datetime.fromisoformat(data['date_created']),
        date_completed=datetime.datetime.fromisoformat(data['date_completed']),
        date_reminded=datetime.datetime.fromisoformat(
          data['date_reminded']) if data['date_reminded'] else None,
        )
    return cls(**data)

  def serialize(self):
    return dict(
        status=self.status,
        id=self.id,
        date_authorized=(self.date_authorized and
          self.date_authorized.isoformat()),
        date_completed=self.date_completed.isoformat(),
        target=self.target.serialize(),
        audience=self.audience,
        actor=self.actor.serialize(),
        note=self.note,
        amount=self.amount,
        action=self.action,
        date_created=self.date_created.isoformat(),
        date_reminded=self.date_reminded and self.date_reminded.isoformat(),
        external_wallet_payment_info=self.external_wallet_payment_info)



@dataclasses.dataclass(frozen=True)
class Transfer:
  type: str
  status: str
  amount: float
  date_requested: datetime.datetime
  amount_cents: int
  amount_fee_cents: int
  amount_requested_cents: int
  payout_id: Optional[str] = None
  date_completed: Optional[datetime.datetime] = None
  source: Optional[FundingSource] = None
  destination: Optional[FundingSource] = None

  @classmethod
  def new(cls, *, type, status, amount, date_requested, amount_cents,
      amount_fee_cents, amount_requested_cents,
      date_completed=None,
      **kwargs):
    transfer_kwargs = {}
    if type == 'add_funds':
      transfer_kwargs['source'] = FundingSource.new(**kwargs['source'])
    elif type == 'destination':
      transfer_kwargs['destination'] = FundingSource.new(**kwargs['destination'])
    date_requested = datetime.datetime.fromisoformat(date_requested)
    if date_completed is not None:
      transfer_kwargs['date_completed'] = datetime.datetime.fromisoformat(date_completed)
      transfer_kwargs['payout_id'] = kwargs['payout_id']
    return cls(type, status, amount, date_requested, amount_cents,
        amount_fee_cents, amount_requested_cents, **transfer_kwargs)

  def serialize(self):
    return dict(
        type=self.type, status=self.status,
        amount=self.amount,
        date_requested=self.date_requested.isoformat(),
        amount_cents=self.amount_cents,
        amount_fee_cents=self.amount_fee_cents,
        amount_requested_cents=self.amount_requested_cents,
        payout_id=self.payout_id,
        date_completed=self.date_completed and self.date_completed.isoformat(),
        source=self.source and self.source.serialize(),
        destination=self.destination and self.destination.serialize())


@dataclasses.dataclass(frozen=True)
class Authorization:
  status: str
  merchant: user_lib.Merchant
  authorization_types: List[str]
  rewards: Optional[str]
  is_venmo_card: bool
  decline: Optional[str]
  payment_method: PaymentMethod
  story_id: str
  created_at: datetime.datetime
  acknowledged: bool
  atm_fees: Optional[str]
  rewards_earned: bool
  descriptor: str
  amount: int
  user: user_lib.User
  captures: List[str]
  id: str
  point_of_sale: Dict[str, Any]

  @classmethod
  def new(cls, *, merchant, payment_method, created_at, user, **kwargs):
    merchant = user_lib.Merchant.new(**merchant)
    payment_method = PaymentMethod.new(**payment_method)
    created_at = datetime.datetime.fromisoformat(created_at)
    user = user_lib.User.new(**user)
    return cls(merchant=merchant, payment_method=payment_method,
        created_at=created_at, user=user, **kwargs)

  def serialize(self):
    return dict(
        status=self.status, merchant=self.merchant.serialize(),
        authorization_types=self.authorization_types,
        rewards=self.rewards,
        is_venmo_card=self.is_venmo_card,
        decline=self.decline,
        payment_method=self.payment_method.serialize(),
        story_id=self.story_id,
        created_at=self.created_at.isoformat(),
        acknowledged=self.acknowledged,
        atm_fees=self.atm_fees,
        rewards_earned=self.rewards_earned,
        descriptor=self.descriptor,
        amount=self.amount,
        user=self.user.serialize(),
        captures=self.captures,
        id=self.id,
        point_of_sale=self.point_of_sale)

@dataclasses.dataclass(frozen=True)
class Capture:
  id: str
  payment_id: str
  amount_cents: int
  authorization_id: str
  datetime_created: datetime.datetime
  top_up: Optional[Dict[str, Any]]
  authorization: Authorization

  @classmethod
  def new(cls, *, id, payment_id, amount_cents, authorization_id, datetime_created, 
      authorization, top_up):
    datetime_created = datetime.datetime.fromisoformat(datetime_created)
    authorization = Authorization.new(**authorization)
    return cls(id, payment_id, amount_cents, authorization_id, datetime_created,
        top_up, authorization)


  def serialize(self):
    return dict(
        id=self.id, payment_id=self.payment_id,
        amount_cents=self.amount_cents, authorization_id=self.authorization_id,
        datetime_created=self.datetime_created.isoformat(),
        top_up=self.top_up,
        authorization=self.authorization.serialize())


TransactionType = Literal[
    'authorization',
    'capture',
    'credit_repayment',
    'credit_repayment_refund',
    'credit_reward',
    'direct_deposit',
    'direct_deposit_reversal',
    'disbursement',
    'dispute',
    'internal_balance_transfer'
    'payment',
    'refund',
    'top_up',
    'transfer',
]


TRANSACTION_MAPPINGS = {
    'authorization': Authorization,
    'capture': Capture,
    'payment': Payment,
    'transfer': Transfer,
}


class Transaction:

  def __init__(self,
      type: TransactionType,
      id: str,
      datetime_created: datetime.datetime,
      note: str,
      amount: float,
      *, 
      funding_source: Optional[FundingSource] = None,
      authorization: Optional[Authorization] = None,
      capture: Optional[Capture] = None,
      credit_repayment: Optional[Any] = None,
      credit_repayment_refund: Optional[Any] = None,
      credit_reward: Optional[Any] = None,
      direct_deposit: Optional[Any] = None,
      direct_deposit_reversal: Optional[Any] = None,
      disbursement: Optional[Any] = None,
      dispute: Optional[Any] = None,
      internal_balance_transfer: Optional[Any] = None,
      payment: Optional[Payment] = None,
      refund: Optional[Any] = None,
      top_up: Optional[Any] = None,
      transfer: Optional[Transfer] = None
      ):
    self.type = type
    self.id = id
    self.datetime_created = datetime_created
    self.note = note
    self.amount = amount
    self.funding_source = funding_source
    self.authorization = authorization
    self.capture = capture
    self.credit_repayment = credit_repayment
    self.credit_repayment_refund = credit_repayment_refund
    self.credit_reward = credit_reward
    self.direct_deposit = direct_deposit
    self.direct_deposit_reversal = direct_deposit_reversal
    self.disbursement = disbursement
    self.dispute = dispute
    self.internal_balance_transfer = internal_balance_transfer
    self.payment = payment
    self.refund = refund
    self.top_up = top_up
    self.transfer = transfer

  @classmethod
  def new(cls, *, type, id, datetime_created, note, amount,
      funding_source = None,**kwargs) -> 'Transaction':
    datetime_created = datetime.datetime.fromisoformat(datetime_created)
    transaction_kwargs = {}
    if type not in TRANSACTION_MAPPINGS:
      raise NotImplementedError(f'Unknown transaction type: {type}, {kwargs[type]}')
    transaction_kwargs[type] = TRANSACTION_MAPPINGS[type].new(**kwargs[type])
    if funding_source is not None:
      funding_source = PaymentMethod.new(**funding_source)
    return cls(type, id, datetime_created, note, amount,
        funding_source=funding_source, **transaction_kwargs)

  def serialize(self):
    serialized_transaction = dict(
        type=self.type,
        id=self.id,
        datetime_created=self.datetime_created.isoformat(),
        note=self.note,
        funding_source=self.funding_source and self.funding_source.serialize(),
        amount=self.amount)
    serialized_transaction[self.type] = getattr(self, self.type).serialize()
    return serialized_transaction

  def __repr__(self):
    return (f'Transaction(type={self.type}, '
            f'id={self.id}, datetime_created={self.datetime_created},'
            f'note={self.note}, amount={self.amount}, '
            f'{self.type}={getattr(self, self.type)})')

  def __eq__(self, other):
    return self.id == other.id

  def __hash__(self):
    return hash(self.id)

