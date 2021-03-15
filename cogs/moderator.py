import discord
import os
import sys
from discord.ext import commands

ROOT = os.path.dirname(sys.modules['__main__'].__file__)


class Moderator(commands.Cog):
  """Moderator command utilities."""
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def blocklist(self, ctx, *, member: discord.Member):
    """Blocklists a user. Blocklisted users cannot use the bot."""
    user = member.id
    with open(os.path.join(ROOT, 'blocklist.txt')) as f:
      blocklist = f.readlines()
      blocklist = [i.strip() for i in blocklist]
      blocklist = [int(i) for i in blocklist]

    if user in blocklist:
      blocklist.remove(user)
      await ctx.send('Removed user from the blocklist.')
    else:
      blocklist.append(user)
      await ctx.send('Added user to the blocklist.')

    with open(os.path.join(ROOT, 'blocklist.txt'), 'w') as f:
      for user in blocklist:
        f.write("{}\n".format(user))

  @commands.command()
  async def ping(self, ctx):
    """A ping function for moderators."""
    await ctx.send('pong')

  async def cog_check(self, ctx):
    """A local check for moderator role."""
    if not isinstance(ctx.channel, discord.abc.GuildChannel):
      return False

    role = discord.utils.get(ctx.author.roles, name='admin')
    return role is not None

  async def cog_command_error(self, ctx, error):
    """Cog error handling."""
    print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))
    await ctx.send('You do not have the necessary permission.')


def setup(bot):
  bot.add_cog(Moderator(bot))
