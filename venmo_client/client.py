from typing import Union

import pathlib
import requests
import json

from venmo_client import model


class VenmoClient:

  def __init__(self,
      config_dir: Union[str, pathlib.Path],
      base_url: str = 'https://api.venmo.com/v1'
      ):
    self.base_url = base_url
    self.session = requests.Session()
    self.config_dir = pathlib.Path(config_dir)
    if self.config_dir:
      if not self.config_dir.exists():
        self.config_dir.mkdir(parents=True, exist_ok=True)
    self.auth_config = None

  @property
  def user_id(self):
    if not self.auth_config:
      raise ValueError('Haven\'t authenticated yet.')
    return self.auth_config['user']['id']

  @property
  def access_token(self):
    if not self.auth_config:
      raise ValueError('Haven\'t authenticated yet.')
    return self.auth_config['access_token']

  def authenticate(self, username: str = None,
                   password: str = None):
    if self.config_dir and (self.config_dir / 'auth.json').exists():
      with open(self.config_dir / 'auth.json', 'r') as fp:
        self.auth_config = json.load(fp)
        return
    if not (username and password):
      raise ValueError('Need to provide username and password.')
    self.auth_config = self.login(username, password)
    with open(self.config_dir / 'auth.json', 'w') as fp:
      json.dump(self.auth_config, fp)

  def login(self, username: str, password: str) -> str:
    payload = dict(
        phone_email_or_username=username,
        client_id='1',
        password=password
    )
    headers = {
        'device-id': '88884260-05O3-8U81-58I1-2WA76F357GR9',
        'Content-Type': 'application/json',
    }
    url = f'{self.base_url}/oauth/access_token'
    req = requests.Request(
        method='POST',
        url=url,
        headers=headers, json=payload).prepare()
    res = self.session.send(req)
    if res.status_code == 201:
      return res.json()
    raise NotImplementedError(res.json())

  def transactions(self, before_id=None, limit: int = 50):
    if not self.access_token:
      raise ValueError('Need to authenticate.')
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/stories/target-or-actor/{self.user_id}'
    params = {
        'before_id': before_id,
        'limit': limit
    }
    req = requests.Request(
        method='GET',
        url=url, headers=headers, params=params).prepare()
    res = self.session.send(req)
    txns = res.json()['data']
    for txn in txns:
      yield model.Transaction.new(**txn)

  def request(self, note, user_id, amount):
    payload = dict(
        note=note,
        metadata=dict(quasi_cash_disclaimer_viewed=False),
        amount=-amount, user_id=user_id,
        audience='private')
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/payments'
    req = requests.Request(
        method='POST',
        url=url,
        headers=headers, json=payload).prepare()
    self.session.send(req)
    return
