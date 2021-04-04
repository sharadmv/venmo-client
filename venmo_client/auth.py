import pathlib
import json

from typing import Union


__all__ = [
    'Config'
]


class Config:
  
  def __init__(self,
      config_dir: Union[str, pathlib.Path]):
    if not config_dir:
      raise ValueError('Must provide a valid config directory')
    self.config_dir = pathlib.Path(config_dir)
    if self.config_dir and not self.config_dir.exists():
      self.config_dir.mkdir(parents=True, exist_ok=True)
    self.auth_file = self.config_dir / 'auth.json'
    self.access_token, self.user_id = None, None
    if self.auth_file.exists():
      with self.auth_file.open('r') as fp:
        auth_json = json.load(fp)
      self.user_id = auth_json['user_id']
      self.access_token = auth_json['access_token']

  def is_authenticated(self) -> bool:
    return self.access_token is not None and self.user_id is not None

  def delete(self):
    self.auth_file.unlink()
    self.user_id = None
    self.access_token = None

  def save(self, user_id: str, access_token: str):
    self.user_id = user_id
    self.access_token = access_token
    with self.auth_file.open('w') as fp:
      json.dump(dict(user_id=user_id, access_token=access_token), fp)

  def get_access_token(self) -> str:
    if not self.access_token:
      raise ValueError('Haven\'t authenticated yet.')
    return self.access_token

  def get_user_id(self) -> str:
    if not self.user_id:
      raise ValueError('Haven\'t authenticated yet.')
    return self.user_id

