from typing import Union

import pathlib
import requests
import uuid
import urllib.parse as urlparse

from venmo_client import auth
from venmo_client import model


class VenmoClient:

  def __init__(self,
      config_dir: Union[str, pathlib.Path],
      base_url: str = 'https://api.venmo.com/v1'
      ):
    self.base_url = base_url
    self.session = requests.Session()
    self.auth_config = auth.Config(pathlib.Path(config_dir))

  @property
  def user_id(self) -> str:
    return self.auth_config.get_user_id()

  @property
  def access_token(self) -> str:
    return self.auth_config.get_access_token()

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
        password=password
    )
    headers = {
        'device-id': str(uuid.uuid4()),#'88884260-05O3-8U81-58I1-2WA76F357GR9',
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
    req = requests.Request(
        method='GET',
        url=url, headers=headers, params=params).prepare()
    res = self.session.send(req).json()
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
    res = self.session.send(req)
    if res.status_code == 204:
      self.auth_config.delete()
      return
    raise ValueError(f'Unable to logout: {res.text}')

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
    headers = {
        'Authorization': f'Bearer {self.access_token}'
    }
    url = f'{self.base_url}/payments'
    req = requests.Request(
        method='POST',
        url=url,
        headers=headers, json=payload).prepare()
    self.session.send(req)
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
