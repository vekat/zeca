import discord
import asyncio

from discord.ext import commands


class Zoeira(commands.Cog):
  """The zuera never ends."""
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='ban', aliases=[])
  async def _ban(self, ctx, *, member: discord.Member):
    """For the craic."""

    author = ctx.author.display_name

    if member in ctx.message.mentions:
      target = member.display_name
    else:
      target = member.mention

    message = '> <:marreta:607695189410054332> **'

    if ctx.author.id == member.id:
      message += author + ' has hammered their thumb. What a shame.'
    elif ctx.author.id == 119819028414857217:
      message += target + ' levou uma marretada! ' + \
          author + ' suspeitou desde o princípio.'
    elif author == 'fausthanos':
      message += target + ' has been slain by Fausthanos, for the good of the Universe.'
    elif author == 'charon':
      message += 'Charon has made a dinner reservation for ' + target + '.'
    elif author == 'winston':
      message += 'Winston has acted upon ' + target + '\'s own actions.'
    else:
      message += author + ' has banned ' + target + '.'

    message += '**'

    await ctx.send(message)

  @commands.command(name='beijunda', aliases=['bd'])
  async def _beijunda(self, ctx, *, member: discord.Member):
    """Manda um beijunda para alguém."""

    if member in ctx.message.mentions:
      target = member.display_name
    else:
      target = member.mention

    message = ':kiss::peach: | **' + ctx.author.display_name + \
        ' mandou um beijunda para ' + target + '**.'

    await ctx.send(message)

  @commands.command(name='shutupvekat')
  @commands.guild_only()
  @commands.cooldown(1, 600, commands.BucketType.guild)
  async def _vekat_suck(self, ctx):
    """Manda o vekat catar coquinhos."""

    vekat = ctx.guild.get_member(119819028414857217)

    if vekat is None:
      print('404 vekat not found')
      return

    embed = discord.Embed(title='Friendly reminder')
    embed.set_image(
        url=
        "https://cdn.discordapp.com/attachments/256903500536086538/413688750007123969/Screenshot_8.png"
    )
    embed.set_footer(text="If vekat doesn't stop after this, you may ban him.")

    await ctx.send(content='Hey ' + vekat.mention, embed=embed)


def setup(bot):
  bot.add_cog(Zoeira(bot))
