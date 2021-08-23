from typing import Optional

import sys
import click
from rich import prompt

from venmo_client import client as vc
from venmo_client import console

def check_if_proper_amount(amount: float):
  if amount <= 0.:
    console.error(f'Must enter positive amount: {amount}')
  #if amount % 0.01 != 0.:
  #  console.error(f'Must enter maximum of two decimal places: {amount}')

def make_client(ctx: click.Context, check_authentication: bool = True) -> vc.VenmoClient:
  config_dir = ctx.obj['config_dir']
  client = vc.VenmoClient(config_dir)
  if check_authentication:
    if not client.is_authenticated():
      console.error(
          'Client not authenticated! '
          'Please run `venmo login`.')
      sys.exit(1)
  return client


@click.group()
@click.option(
    '--config-dir',
    type=str,
    default='.venmo-config',
    help='Directory for Venmo authentication information')
@click.pass_context
def cli(ctx: click.Context, config_dir: str = '.venmo-config'):
  ctx.ensure_object(dict)
  ctx.obj['config_dir'] = config_dir
  

@cli.command()
@click.option('--username',
    type=str,
    default=None,
    help='Venmo username')
@click.option('--password',
    type=str,
    default=None,
    help='Venmo password')
@click.pass_context
def login(ctx: click.Context, *, username: Optional[str], password:
    Optional[str]):
  client = make_client(ctx, check_authentication=False)
  if not username:
    username = prompt.Prompt.ask('Enter username')
  if not password:
    password = prompt.Prompt.ask('Enter password', password=True)
  with console.status('Authenticating...'):
    client.authenticate(username=username, password=password)
  console.print('[bold green]Successfully authenticated!')


@cli.command()
@click.pass_context
def logout(ctx: click.Context):
  client = make_client(ctx, check_authentication=False)
  with console.status('Logging out...'):
    client.logout()
  console.print('[bold green]Logged out successfully!')


@cli.command()
@click.option('--username',
    type=str,
    default=None,
    help='Venmo username to charge')
@click.option('--amount',
    type=float,
    default=None,
    help='Amount to charge')
@click.option('--memo',
    type=str,
    default=None,
    help='Memo for Venmo charge')
@click.pass_context
def charge(ctx: click.Context, username: Optional[str], amount: Optional[float],
    memo: Optional[str]):
  client = make_client(ctx)
  if not username:
    username = prompt.Prompt.ask('Enter username to charge')
    if not username:
      console.error('Please enter username.')
  if not amount:
    amount = prompt.FloatPrompt.ask('Enter amount to charge')
    check_if_proper_amount(amount)
  if not memo:
    memo = prompt.Prompt.ask('Enter charge memo')
    if not memo:
      console.error('Please enter memo.')
  usernames = username.split(',')
  for username in usernames:
    client.request(memo, username, amount)
    console.print(f'[bold green]Charged {username} successfully!')
