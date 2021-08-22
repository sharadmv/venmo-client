import sys

from rich import console as cs

console = cs.Console()

def print(*args, **kwargs):
  return console.print(*args, **kwargs)

def rule(*args, **kwargs):
  return console.rule(*args, **kwargs)

def status(*args, **kwargs):
  return console.status(*args, **kwargs)

def error(message: str):
  console.print(f'[bold red]{message}')
  sys.exit(1)
