import locale
import sys

from typing import Optional

import click
from rich import prompt
from rich import table

from venmo_client import client as vc
from venmo_client import console

locale.setlocale(locale.LC_ALL, '')


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
  client = make_client(ctx, check_authentication=True)
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
    with console.status(f'Charging [bold]{username}'):
      client.request(memo, username, amount)
    console.print(f'[bold green]Charged {username} successfully!')

@cli.command()
@click.pass_context
@click.option('--action',
    default='charge',
    help='Payment action')
@click.option('--cancelled/--no-cancelled',
    default=False,
    help='Include cancelled transactions')
@click.option('--pending/--no-pending',
    default=False,
    help='Include pending transactions')
@click.option('--settled/--no-settled',
    default=False,
    help='Include settled transactions')
@click.option('--limit',
    default=50,
    help='Maximum number of payments',
    type=int)
def payments(ctx: click.Context, action: str, cancelled: bool,
    pending: bool, settled: bool, limit: int):
  client = make_client(ctx, check_authentication=True)
  tab = table.Table(show_header=True, header_style="bold")
  tab.add_column("Date", style='dim')
  tab.add_column("Name")
  tab.add_column("Amount", style='green', justify='right')
  tab.add_column("Memo")
  tab.add_column("Reminded?")
  tab.add_column("Status", style='dim')

  status = ()
  if pending:
    status += ('held', 'pending')
  if cancelled:
    status += ('cancelled',)
  if settled:
    status += ('settled',)
  with console.status('Loading payments'):
    for txn in client.payments(status=status, limit=limit, action=action):
      has_reminded = bool(txn.date_reminded)
      date_requested = txn.date_created
      status = txn.status
      tab.add_row(
          date_requested.strftime('%m/%d/%y'), txn.target.user.display_name,
          f'{locale.currency(txn.amount)}', txn.note,
          '[green]Yes[/green]'
          if has_reminded else '[red]No[/red]',
          txn.status)
  console.print(tab)

@cli.command()
@click.pass_context
@click.option('--limit',
    default=50,
    help='Maximum number of payments',
    type=int)
def notifications(ctx: click.Context, limit: int):
  client = make_client(ctx, check_authentication=True)
  tab = table.Table(show_header=True, header_style="bold")
  tab.add_column("Date", style='dim')
  tab.add_column("Type")
  tab.add_column("Message")

  with console.status('Loading notifications'):
    for txn in client.notifications(limit=limit):
      tab.add_row(
          txn.date_created.strftime('%m/%d/%y'),
          txn.type,
          txn.message)
  console.print(tab)

@cli.command()
@click.pass_context
@click.option('--limit',
    default=50,
    help='Maximum number of notifications',
    type=int)
def settle(ctx: click.Context, limit: int):
  client = make_client(ctx, check_authentication=True)
  with console.status('Loading notifications'):
    notifs = list(client.notifications(limit=limit))

  for i, notif in enumerate(notifs):
    date = notif.date_created.strftime('%m/%d/%y')
    console.print(f'[bold]{i + 1}>[/] [dim]{date}[/]: {notif.message}')
  valid_choices = set(range(1, len(notifs) + 1))
  pick = prompt.IntPrompt.ask('Which notification?', choices=list(map(str,
    valid_choices)))
  notif = notifs[pick - 1]
  client.settle(notif.payment.id)
