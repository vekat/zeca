import sys
import os
import re
import time
import signal

import discord
import asyncio

import private

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

    self.main_guild = private.guild
    self.dialect_channel = private.dialect
    self.proficiency_channel = private.proficiency
    self.welcome_hook = private.welcome

    self.setup_blacklist()
    self.add_check(self.is_main_guild)

  def setup_blacklist(self):
    self.blacklist_path = private.blacklist_path
    self.load_blacklist()
    self.add_check(self.is_not_blacklisted)

  def load_blacklist(self):
    blp = Path(self.blacklist_path)
    if not blp.exists():
      blp.touch()

    with blp.open() as blf:
      self.blacklisted_ids = [int(l.strip()) for l in blf.readlines()]

  def is_main_guild(self, ctx):
    return ctx.guild and ctx.guild.id == self.main_guild.id

  def is_not_blacklisted(self, ctx):
    return ctx.author and ctx.author.id not in self.blacklisted_ids

  async def on_ready(self):
    print(f'→ login successful as: {self.user}')
    print(f'→ discord.py version: {discord.__version__}')

    if type(self.welcome_hook) is int:
      self.welcome_hook = await self.fetch_webhook(self.welcome_hook)

    if type(self.main_guild) is int:
      self.main_guild = self.get_guild(self.main_guild)

    if type(self.dialect_channel) is int:
      self.dialect_channel = self.get_channel(self.dialect_channel)

    if type(self.proficiency_channel) is int:
      self.proficiency_channel = self.get_channel(self.proficiency_channel)

  async def on_member_join(self, member):
    member_id = member.id
    member_name = str(member)
    if self.name_filter.findall(member_name):
      return await member.ban(reason=f'[{self.user}] blacklisted name')

    await asyncio.sleep(private.welcome_delay)

    if not self.main_guild.get_member(member_id):
      return

    return await self.welcome_hook.send(
        content=private.welcome_message.format(client=self, member=member)
    )


def exit_gracefully(signum, frame):
  signal.signal(signal.SIGINT, original_sigint)

  bot.close()

  signal.signal(signal.SIGINT, exit_gracefully)
  
  sys.exit()


if __name__ == '__main__':
  original_sigint = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, exit_gracefully)

  bot = Zeca(
      command_prefix='>',
      intents=intents,
      activity=discord.Activity(
          name='Never gonna give you up', type=discord.ActivityType.listening
      ),
      allowed_mentions=discord.AllowedMentions(
        users=True,
        everyone=False,
        roles=False,
        replied_user=True,
      )
  )

  exts = ['cogs.utilities']

  for ext in exts:
    try:
      bot.load_extension(ext)
    except Exception as err:
      print(f'→ error loading extension {ext}')
      print(err)

  bot.run(private.TOKEN)
