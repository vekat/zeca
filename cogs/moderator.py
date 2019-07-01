import discord
import os
import sys
from discord.ext import commands

ROOT = os.path.dirname(sys.modules['__main__'].__file__)

class Moderator:
    """Moderator command utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def blacklist(self, ctx, *, member: discord.Member):
        """Blacklists a user. Blacklisted users cannot use the bot."""
        user = member.id
        with open(os.path.join(ROOT, 'blacklist.txt')) as f:
            blacklist = f.readlines()
            blacklist = [i.strip() for i in blacklist]
            blacklist = [int(i) for i in blacklist]

        if user in blacklist:
            blacklist.remove(user)
            await ctx.send('Removed user from the black list.')
        else:
            blacklist.append(user)
            await ctx.send('Added user to the black list.')

        with open(os.path.join(ROOT, 'blacklist.txt'), 'w') as f:
            for user in blacklist:
                f.write("{}\n".format(user))


    @commands.command()
    async def ping(self, ctx):
        """A ping function for moderators."""
        await ctx.send('pong')

    async def __local_check(self, ctx):
        """A local check for moderator role."""
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False

        role = discord.utils.get(ctx.author.roles, name='admin')
        return role is not None

    async def __error(self, ctx, error):
        """Cog error handling."""
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))
        await ctx.send('You do not have the necessary permission.')


def setup(bot):
    bot.add_cog(Moderator(bot))
