import sys
import os
import re
import time
from datetime import datetime

import discord
import asyncio

from discord.ext import commands

import private
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

    await self.remove_temp_roles()

  async def remove_temp_roles(self):
    # removes the hitmeup role from everyone who has it
    guild = self.guilds[0]
    role = discord.utils.get(guild.roles, name='hit me up')
    try:
      for member in role.members or []:
        await member.remove_roles(role)
        await member.send(utilities.Utilities.expired_role_msg)
    except discord.DiscordException:
      pass  # ignores this if no one has the hitmeup role

  async def load_blacklist(self):
    # load blacklisted users
    try:
      with open(os.path.join(ROOT, 'blacklist.txt')) as f:
        self.blacklist = [int(i.strip()) for i in f.readlines()]
        print('blacklisted IDs:')
        print(blacklist)
    except FileNotFoundError:
      with open(os.path.join(ROOT, 'blacklist.txt'), 'w') as f:
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
        title="<:pt:589471198107402240> While you wait...",
        colour=discord.Colour(0x9b3a),
        description="You might want to read our rules in " +
        rules_channel.mention,
        timestamp=datetime.utcfromtimestamp(time.time())
    )

    embed.add_field(
        name="Getting started",
        value=
        "• First get a proficiency role in <#607329738012491793>\n• Then an optional dialect role in <#607330935133700146>\n\nOr type role commands here, as explained in "
        + roles_channel.mention
    )

    if welcome_channel:
      await welcome_channel.send(
          content="Hi " + member.mention + ", welcome to **Portuguese**",
          embed=embed
      )


if __name__ == '__main__':
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
