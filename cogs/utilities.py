import discord
import dicinformal
import priberamdict
import asyncio
import re
import private

from discord.ext import commands
from highlighter import compare_texts
from urbandic import UDQuery


def inv_dict(d, r, prefix=None):
  for key, lst in d.items():
    for val in lst:
      if prefix:
        r[prefix + val] = key
      r[val] = key


class Utilities(commands.Cog):
  """Member utilities."""
  def __init__(self, bot):
    self.bot = bot

  level_roles = {}
  country_roles = {}
  other_roles = {}

  inv_dict(private.level_roles_aliases, level_roles, 'level ')
  inv_dict(private.country_roles_aliases, country_roles)
  inv_dict(private.other_roles_aliases, other_roles)

  public_roles = {**level_roles, **country_roles, **other_roles}

  @commands.command(name='role', aliases=['r'])
  async def _role(self, ctx, *, rolearg):
    """
    Assigns or removes a role.

    If role is a level role (Level A, Level B, Level C, or Native),
    the previous level will be automatically removed.

    The role 'hit me up' expires after 1 hour.

    Sub-command:
        list:  Shows a list of public roles.
    """

    rolearg = rolearg.lower()
    if rolearg in list(self.public_roles.keys()):
      roleid = self.public_roles[rolearg]
      role = await commands.RoleConverter().convert(ctx, roleid)
      member = ctx.author
      if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(private.emojis['confirm'] + ' cargo adicionado.')
      else:
        if roleid in list(self.level_roles.values()):
          for a, r in enumerate(member.roles):
            if str(r.id) in list(self.level_roles.values()):
              await member.remove_roles(r)

        await member.add_roles(role)
        await ctx.send(private.emojis['confirm'] + ' cargo removido.')
    elif rolearg == 'list':
      output = 'cargos disponíveis (e aliases):\n' + '```' + \
               ', '.join(
                   list(dict.fromkeys(self.public_roles.keys()))) + '```'
      await ctx.send(output)
    else:
      raise commands.BadArgument

  @_role.error
  async def _role_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send(
          private.emojis['error'] +
          ' esse cargo ou não existe, ou não é público.' +
          ' *please, check your spelling*.'
      )

  @commands.command(name='dicinf', aliases=['di', 'dicinformal'])
  async def _dicionarioinformal(self, ctx, *term):
    """
    Looks a word up in the Dicionário Informal.

    Don't trust this dictionary blindly. It's like a Brazilian Urban Dictionary.
    """
    def _meaning(entry):
      result = dicinformal.Query(entry)
      embed = discord.Embed(
          title=result.term,
          url=result.url,
          description=result.description,
          color=0x3498DB
      )
      embed.set_footer(icon_url=result.favicon, text=result.disclaimer)
      return embed

    term = ' '.join(term)
    commands_channel = self.bot.get_channel(int(private.welcome))
    await commands_channel.send(ctx.author.mention, embed=_meaning(term))

  @_dicionarioinformal.error
  async def _dicionarioinformal_error(self, ctx, error):
    if isinstance(error, commands.CommandInvokeError):
      pass
      # await ctx.send(error.__cause__)
      # await ctx.send(':exclamation: no results found.')

  @commands.command(name='priberam', aliases=['pri'])
  async def _priberam(self, ctx, *, entry):
    """
    Looks up a word in the Priberam Portuguese dictionary.

    The definitions and examples might be in pre-1990 Agreement
    Portuguese. Make sure to check the footer for possible changes.

    https://www.priberam.pt/
    https://en.wikipedia.org/wiki/Portuguese_Language_Orthographic_Agreement_of_1990
    """
    results = priberamdict.Entry(entry)
    d = results.definitions
    s = results.suggestions

    if d:
      output = d[0]
      t = results.table_of_contents[0]
      if t['affect']:
        output = output + '_Após o acordo ortográfico:_ **' + \
            t['br_aft'] + '** 🇧🇷, **' + t['pt_aft'] + '** 🇵🇹.\n'
      else:
        output = output + '_Grafias:_ **' + \
            t['br_bef'] + '** 🇧🇷, **' + t['pt_bef'] + '** 🇵🇹.\n'

    if isinstance(s, list):
      output = 'Palavra não encontrada. '
      if s:
        output = output + 'Aqui estão algumas sugestões:\n'
        output = output + ' '.join(s)

    commands_channel = self.bot.get_channel(int(private.welcome))
    await commands_channel.send(ctx.author.mention + '\n' + output)

  @_priberam.error
  async def __priberam_error(self, ctx, error):
    pass

  @commands.command(name='correct', aliases=['c'])
  async def _correct_message(self, ctx, message_id, *, correction):
    """
    Highlights the mistakes in a members message provided the message ID followed by the correction.

    - The author of the message you want to correct must have the "Correct me" role.
    - To get the ID of a message you have to right click the message and then click "Copy ID".
    - To see the "Copy ID" option you must activate the developer mode.
        Go to your Settings > Appearance > Advanced > Developer Mode
    """
    target_msg = await ctx.channel.get_message(message_id)
    target_user = target_msg.author

    role = discord.utils.get(target_user.roles, name='correct me')

    if role is not None:
      mistakes, corrected = compare_texts(target_msg.content, correction)
      output = '{}, {} has corrected your message!\n> {}\n{}\n'.format(
          target_user.mention, ctx.author.display_name, mistakes, corrected
      )
      await ctx.send(output)
    else:
      await ctx.send(
          'The author of the message you want to correct ' +
          'must have a "correct me" role.'
      )
    await asyncio.sleep(3)
    await ctx.message.delete()

  @commands.command(name='urbandictionary', aliases=['urban', 'ud'])
  async def _urbandictionary(self, ctx, *, entry):
    """
    Look up a word in the Urban Dictionary.
    """
    query = UDQuery(entry)
    definition = query.definition
    definition = re.sub(r'[\[\]]', '', definition)  # Remove [ and ] chars
    embed = discord.Embed(
        title=query.entry,
        url=query.permalink,
        description=definition,
        color=0x3498DB
    )
    embed.set_footer(icon_url=query.favicon, text=query.disclaimer)

    commands_channel = self.bot.get_channel(int(private.welcome))
    await commands_channel.send(ctx.author.mention, embed=embed)


def setup(bot):
  bot.add_cog(Utilities(bot))
