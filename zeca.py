import sys
import os
import re
import time
import signal

import discord
import asyncio

from private import TOKEN
from constants import *

from pathlib import Path
from datetime import datetime
from discord.ext import commands

ROOT = os.path.dirname(sys.modules['__main__'].__file__)

intents = discord.Intents.default()
intents.members = True


class Zeca(commands.Bot):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.name_filter = re.compile(r'discord\.gg/\S+', re.I)

    self.main_guild = None
    self.dialect_channel = None
    self.proficiency_channel = None
    self.welcome_hook = None

    self.setup_blocklist()
    self.add_check(self.is_main_guild)

  def setup_blocklist(self):
    self.blocklist_path = blocklist_path
    self.load_blocklist()
    self.add_check(self.is_not_blocklisted)

  def load_blocklist(self):
    blocklist_path = Path(self.blocklist_path)
    if not blocklist_path.exists():
      blocklist_path.touch()

    with blocklist_path.open() as blocklist_file:
      self.blocklisted_ids = [int(l.strip()) for l in blocklist_file.readlines()]

  def is_main_guild(self, ctx):
    try:
      return ctx.guild and ctx.guild.id == self.main_guild.id
    except AttributeError:
      print('Looks like your guild id is configured incorrectly.')


  def is_not_blocklisted(self, ctx):
    return ctx.author and ctx.author.id not in self.blocklisted_ids

  async def on_ready(self):
    print(f'→ login successful as: {self.user}')
    print(f'→ discord.py version: {discord.__version__}')

    if not self.main_guild:
      self.main_guild = self.get_guild(guild_id)
      if not self.main_guild:
        print('The guild/server was not found. Check the guild id.')

    if not self.welcome_hook:
      try:
        self.welcome_hook = await self.fetch_webhook(welcome_webhook_id)
      except:
        print('The welcome webhook was not found!')

    if not self.dialect_channel:
      self.dialect_channel = self.get_channel(channels['dialect'])
      if not self.dialect_channel:
        print('The dialect channel was not found. Check the id.')

    if not self.proficiency_channel:
      self.proficiency_channel = self.get_channel(channels['proficiency'])
      if not self.proficiency_channel:
        print('The proficiency channel was not found. Check the id.')

  async def on_member_join(self, member):
    member_id = member.id
    member_name = str(member)
    if self.name_filter.findall(member_name):
      return await member.ban(reason=f'[{self.user}] blocklisted name')

    await asyncio.sleep(welcome_delay)

    if not self.main_guild.get_member(member_id):
      return

    return await self.welcome_hook.send(
      content=welcome_message.format(client=self, member=member)
    )


def exit_gracefully(signum, frame):
  signal.signal(signal.SIGINT, original_sigint)

  bot.close()
  sys.exit()

  signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == '__main__':
  original_sigint = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, exit_gracefully)

  bot = Zeca(
      command_prefix='>',
      intents=intents,
      activity=discord.Activity(
          name='Never gonna give you up', type=discord.ActivityType.listening
      )
  )

  exts = ['cogs.moderator', 'cogs.utilities', 'cogs.zoeira']

  for ext in exts:
    try:
      bot.load_extension(ext)
    except Exception as err:
      print(f'→ error loading extension {ext}')
      print(err)

  bot.run(TOKEN)
