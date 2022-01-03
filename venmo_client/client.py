import datetime

from typing import Optional, Union

import pathlib
import requests
from rich import prompt
import uuid
import urllib.parse as urlparse

from venmo_client import auth
from venmo_client import model
from venmo_client import util

TRANSACTION_HISTORY_URL = 'https://venmo.com/transaction-history/statement?startDate={start_date}&endDate={end_date}&profileId={user_id}&accountType=personal'

class VenmoClient:

  def __init__(self,
      config_dir: Union[str, pathlib.Path],
      base_url: str = 'https://api.venmo.com/v1',
      ):
    self.base_url = base_url
    self.session = requests.Session()
    self.auth_config = auth.Config(pathlib.Path(config_dir))
    self.device_id = str(uuid.uuid4())

  @property
  def user_id(self) -> str:
    return self.auth_config.get_user_id()

  @property
  def access_token(self) -> str:
    return self.auth_config.get_access_token()

  def is_authenticated(self):
    return self.auth_config.is_authenticated()

  def _make_request(self, url, method, *, headers={}, payload={}, params={}) -> requests.Response:
    req = requests.Request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=payload).prepare()
    return self.session.send(req)

  def authenticate(self, *,
      username: str = None,
      password: str = None):
    if self.auth_config.is_authenticated():
      return
    if not (username and password):
      raise ValueError('Need to provide username and password.')
    auth_json = self.login(username, password)
    self.auth_config.save(
        auth_json['user']['id'],
        auth_json['access_token'])

  def login(self, username: str, password: str) -> str:
    payload = dict(
        phone_email_or_username=username,
        client_id='1',
        password=password,
    )
    headers = {
        'device-id': self.device_id,
        'Content-Type': 'application/json',
    }
    url = f'{self.base_url}/oauth/access_token'
    res = self._make_request(url, 'POST', headers=headers, payload=payload)
    if res.status_code == 201:
      return res.json()
    elif res.status_code == 401:
      venmo_otp_secret = res.headers['venmo-otp-secret']
      return self.login_with_text(username, password, venmo_otp_secret)
    else:
      message = res.json()
      if 'error' in message:
        raise ValueError(message['error']['message'])
    raise NotImplementedError(res.json())

  def login_with_text(self, username, password, secret):
    headers = {
      'device-id': self.device_id,
      'venmo-otp-secret': secret,
      'Content-Type': 'application/json'
    }
    payload = dict(via='sms')
    url = f'{self.base_url}/account/two-factor/token'
    res = self._make_request(url, 'POST', headers=headers, payload=payload)
    if res.status_code != 200:
      raise ValueError('Failed to send text')
    code = prompt.Prompt.ask('Enter code')

    headers = {
      'device-id': self.device_id,
      'venmo-otp-secret': secret,
      'Venmo-Otp': code
    }
    url = f'{self.base_url}/oauth/access_token?client_id=1'
    res = self._make_request(url, 'POST', headers=headers, payload=payload)
    if res.status_code != 201:
      raise ValueError(res.status_code)
    return res.json()

  def transactions(self, before_id=None, limit: int = 50, **kwargs):
    if not self.access_token:
      raise ValueError('Need to authenticate.')
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/stories/target-or-actor/{self.user_id}'
    params = {
        'before_id': before_id,
        'limit': limit,
        **kwargs
    }
    res = self._make_request(url, 'GET', headers=headers, params=params).json()
    pagination = res['pagination']
    parsed_url = urlparse.urlparse(pagination['next'])
    qs = urlparse.parse_qs(parsed_url.query)
    txns = (model.Transaction.new(**d) for d in res['data'])
    yield txns
    yield from self.transactions(**qs)

  def logout(self):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/oauth/access_token'
    req = requests.Request(
        method='DELETE',
        url=url,
        headers=headers).prepare()
    res = self._make_request(url, 'DELETE', headers=headers)
    if res.status_code == 204:
      self.auth_config.delete()
      return
    raise ValueError(f'Unable to logout: {res.text}')

  def me(self):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/me'
    res = self._make_request(url, 'GET', headers=headers)
    if res.status_code == 200:
      result = res.json()['data']
      user = model.User(**result['user'])
      return dict(result, user=user)

  def balance(self):
    me = self.me()
    return float(me['balance'])

  def get_user_id(self, username):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/users/{username}'
    res = self._make_request(url, 'GET', headers=headers)
    if res.status_code == 200:
      return res.json()['data']['id']
    print(res.json())
    raise ValueError(res.status_code)

  def get_transaction(self, transaction_id):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/stories/{transaction_id}'
    res = self._make_request(url, 'GET', headers=headers)
    if res.status_code == 200:
      return res.json()['data']
    print(res.json())
    raise ValueError(res.status_code)

  def get_transaction_history(
      self,
      *,
      start_date: Optional[Union[str, datetime.date]] = None,
      end_date: Optional[Union[str, datetime.date]] = None):
    if not start_date:
      start_date = datetime.date.today() - datetime.timedelta(days=90)
    if not end_date:
      end_date = datetime.date.today()
    start_date = util.canonicalize_date(start_date)
    end_date = util.canonicalize_date(end_date)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    url = f'{self.base_url}/transaction-history'
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    params = {
        'start_date': start_date_str,
        'end_date': end_date_str,
        'profile_id': self.user_id,
        'account_type': 'personal'
    }
    res = self._make_request(url, 'GET', headers=headers, params=params)
    if res.status_code != 200:
      print(res.json())
      raise ValueError(res.status_code)
    results = res.json()
    start_balance = results['data']['start_balance']
    end_balance = results['data']['end_balance']
    transactions = results['data']['transactions']
    parsed_transactions = []
    for txn in transactions:
      parsed_transactions.append(model.Transaction.new(**txn))
    return parsed_transactions, (start_balance, end_balance)
#
  def request(self, note, username, amount):
    user_id = self.get_user_id(username)
    payload = dict(
        note=note,
        metadata=dict(quasi_cash_disclaimer_viewed=False),
        amount=-amount, user_id=user_id,
        audience='private')
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/payments'
    res = self._make_request(url, 'POST', headers=headers, payload=payload)
    if res.status_code != 200:
      print(res.json())
      raise ValueError(res.status_code)
    return

  def payments(self, action='charge', status=(), limit=None, before=None):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/payments'
    params = {
        'action': action,
        'status': ','.join(status),
        'limit': limit,
        'before': before
    }
    res = self._make_request(url, 'GET', headers=headers, params=params)
    if res.status_code != 200:
      raise ValueError(res.status_code)
    res = res.json()
    data = res['data']
    for txn in data:
      yield model.Payment.new(**txn)
    pagination = res['pagination']
    if pagination:
      parsed_url = urlparse.urlparse(pagination['next'])
      qs = urlparse.parse_qs(parsed_url.query)
      limit = int(qs.pop('limit')[0])
      if limit - len(data) > 0:
        yield from self.payments(**qs, status=status, limit=limit - len(data))

  def notifications(self, limit = None):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/notifications'
    params = {
        'limit': limit,
        'status': 'incoming',
    }
    res = self._make_request(url, 'GET', headers=headers, params=params)
    if res.status_code != 200:
      raise ValueError(res.status_code)
    res = res.json()
    data = res['data']
    for txn in data:
      txn = model.Notification.new(**txn)
      if txn.type == 'venmo_card_shipped':
        continue
      yield txn

    pagination = res['pagination']
    if 'next' in pagination:
      parsed_url = urlparse.urlparse(pagination['next'])
      qs = urlparse.parse_qs(parsed_url.query)
      limit = int(qs.pop('limit')[0])
      if limit - len(data) > 0:
        yield from self.payments(**qs, limit=limit - len(data))

  def settle(self, payment_id: str):
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/payments/{payment_id}'
    payload = dict(
        action='pay',
        actor=self.user_id,
        funding_source_id="1075861407137792751"
    )
    res = self._make_request(url, 'PUT', headers=headers, payload=payload)
    if res.status_code != 200:
      print(res.text)
      raise ValueError(res.status_code)
    res = res.json()
    print(res)
