import dataclasses
import datetime

from typing import Any, Dict, List, Literal, Optional

from venmo_client.model import user

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
  def new(cls, **data):
    data = dict(data,
        transfer_to_estimate=datetime.datetime.fromisoformat(data['transfer_to_estimate']))
    return cls(**data)


@dataclasses.dataclass(frozen=True)
class Target:
  type: str
  phone: Optional[str]
  email: Optional[str]
  redeemable_target: Optional[str]
  user: Optional['user.User'] = None
  merchant: Optional[str] = None

  @classmethod
  def new(cls, *, type, phone, email, redeemable_target, **kwargs):
    target_kwargs = {}
    if type == 'user':
      target_kwargs['user'] = user.User.new(**kwargs['user'])
    else:
      raise NotImplementedError(f'Unknown target type: {type}')
    return cls(type, phone, email, redeemable_target, **target_kwargs)


@dataclasses.dataclass(frozen=True)
class Payment:
  status: str
  id: str
  date_authorized: Optional[datetime.datetime]
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
class Transfer:
  status: str
  source: FundingSource
  amount: float
  date_requested: datetime.datetime
  amount_cents: int
  amount_fee_cents: int
  payout_id: str
  date_completed: datetime.datetime
  amount_requested_cents: int
  type: str

  @classmethod
  def new(cls, **data):
    print(data['source'])
    data = dict(data,
        source=FundingSource.new(**data['source']),
        date_requested=datetime.datetime.fromisoformat(data['date_requested']),
        date_completed=datetime.datetime.fromisoformat(data['date_completed']))
    return cls(**data)



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

Authorization = Capture = CreditRepayment = \
CreditRepaymentRefund = CreditReward = DirectDeposit = DirectDepositReversal = \
Disbursement = Dispute = InternalBalanceTransfer = Refund = TopUp = Any

TRANSACTION_MAPPINGS = {
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
      credit_repayment: Optional[CreditRepayment] = None,
      credit_repayment_refund: Optional[CreditRepaymentRefund] = None,
      credit_reward: Optional[CreditReward] = None,
      direct_deposit: Optional[DirectDeposit] = None,
      direct_deposit_reversal: Optional[DirectDepositReversal] = None,
      disbursement: Optional[Disbursement] = None,
      dispute: Optional[Dispute] = None,
      internal_balance_transfer: Optional[InternalBalanceTransfer] = None,
      payment: Optional[Payment] = None,
      refund: Optional[Refund] = None,
      top_up: Optional[TopUp] = None,
      transfer: Optional[Transfer] = None
      ):
    self.type = type
    self.id = id
    self.datetime_created = datetime_created
    self.note = note
    self.amount = amount
    self.funding_source = funding_source
    self.authorization = authorization
    self.capture = capture,
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
  def new(cls, *, type, id, datetime_created, note, amount, **kwargs) -> 'Transaction':
    datetime_created = datetime.datetime.fromisoformat(datetime_created)
    transaction_kwargs = {}
    if type not in TRANSACTION_MAPPINGS:
      raise NotImplementedError(f'Unknown transaction type: {type}')
    transaction_kwargs[type] = TRANSACTION_MAPPINGS[type].new(**kwargs[type])
    return cls(type, id, datetime_created, note, amount, **transaction_kwargs)

  def __repr__(self):
    return f'Transaction(type={self.type}, id={self.id}, datetime_created={self.datetime_created}, note={self.note}, amount={self.amount}, {self.type}={getattr(self, self.type)})'
