import sys
import os
import re
import time
import signal

import discord
import asyncio

import private

from datetime import datetime
from discord.ext import commands
from cogs import utilities

ROOT = os.path.dirname(sys.modules['__main__'].__file__)
name_filter = re.compile(r'discord\.gg/\S+', re.I)


class Zeca(commands.Bot):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.blacklist = []
    self.add_check(self.check_user)

  async def on_ready(self):
    print('• logged on as:', self.user)
    print('• discord.py version:', discord.__version__)

    await self.load_blacklist()

  async def load_blacklist(self):
    # load blacklisted users
    try:
      with open(os.path.join(ROOT, 'blacklist.txt')) as f:
        self.blacklist = [int(i.strip()) for i in f.readlines()]
        print('blacklisted IDs:')
        print(self.blacklist)
    except FileNotFoundError:
      with open(os.path.join(ROOT, 'blacklist.txt'), 'w') as f:
        self.blacklist = []
        pass

  def check_user(self, ctx):
    return ctx.author.id not in self.blacklist

  async def on_member_join(self, member):
    mid = member.id
    guild = member.guild

    member_name = str(member)
    if name_filter.findall(member_name):
      return await member.ban(reason="[zeca] banned for blacklisted name")

    welcome_channel = guild.get_channel(private.welcome)
    rules_channel = guild.get_channel(private.rules)
    roles_channel = guild.get_channel(private.roles)

    await asyncio.sleep(private.delay)

    if not guild.get_member(mid):
      return

    embed = discord.Embed(
        title="<:pt:589471198107402240> Getting started",
        colour=discord.Colour(0x9b3a),
        description="Please, read our " + rules_channel.mention,
        timestamp=datetime.utcfromtimestamp(time.time())
    )

    embed.add_field(
        name="Get your roles",
        value=
        "• First get a proficiency role in <#607329738012491793>\n• Then an optional dialect role in <#607330935133700146>\n\nOr type *role commands* here, as explained in "
        + roles_channel.mention
    )

    if welcome_channel:
      await welcome_channel.send(
          content="Oi " + member.mention + ", welcome to **Portuguese**",
          embed=embed
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
      activity=discord.Activity(
          name='Never gonna give you up', type=discord.ActivityType.listening
      )
  )

  extensions = ['cogs.moderator', 'cogs.utilities', 'cogs.zoeira']

  for e in extensions:
    try:
      bot.load_extension(e)
    except:
      print('• failed to load {}'.format(e))

  bot.run(private.TOKEN)
