import discord
import dicinformal
import priberamdict
import dictionary_scraper as ds
import asyncio
import re
import private

from typing import Optional
from typing_extensions import Literal

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

    self.member_role = private.member_role
    self.nolevel_role = private.nolevel_role
    self.commands_channel = private.commands

  level_roles = {}
  country_roles = {}
  other_roles = {}

  inv_dict(private.level_roles_aliases, level_roles, 'level ')
  inv_dict(private.country_roles_aliases, country_roles)
  inv_dict(private.other_roles_aliases, other_roles)

  public_roles = {**level_roles, **country_roles, **other_roles}

  @commands.Cog.listener()
  async def on_ready(self):
    if type(self.commands_channel) is int:
      self.commands_channel = self.bot.get_channel(self.commands_channel)

    guild = self.bot.guilds[0]

    if type(self.member_role) is int:
      self.member_role = guild.get_role(self.member_role)

    if type(self.nolevel_role) is int:
      self.nolevel_role = guild.get_role(self.nolevel_role)

    self.done_emoji = '👍'
    self.error_emoji = '👎'

    for e in guild.emojis:
      if e.id == private.emojis['error']:
        self.error_emoji = e
      elif e.id == private.emojis['confirm']:
        self.done_emoji = e

  def to_lower(arg):
    return arg.lower()

  @commands.command(name='role', aliases=['r'])
  @commands.cooldown(4, 60.0, commands.BucketType.user)
  async def _role(self, ctx, *, args: to_lower):
    """
    Assigns or removes a role.

    If role is a level role (Level A, Level B, Level C, or Native),
    the previous level will be automatically removed.

    Sub-command:
        list:  Shows a list of public roles.
    """
    output = None

    if args in list(self.public_roles.keys()):
      roleid = self.public_roles[args]
      role = await commands.RoleConverter().convert(ctx, roleid)
      member = ctx.author

      if role in member.roles:
        await member.remove_roles(role)
        if roleid in list(self.level_roles.values()):
          await member.add_roles(self.nolevel_role)
        output = f'cargo `{role.name}` removido'
      else:
        if roleid in list(self.level_roles.values()):
          for a, r in enumerate(member.roles):
            if str(r.id) in list(self.level_roles.values()):
              await member.remove_roles(r)
          if self.nolevel_role in member.roles:
            await member.remove_roles(self.nolevel_role)

        await member.add_roles(role, self.member_role)
        output = f'cargo `{role.name}` adicionado'
    elif args == 'list':
      output = f"cargos disponíveis:\n```{', '.join(list(dict.fromkeys(self.public_roles.keys())))}```"

    if output is None:
      raise commands.BadArgument

    await ctx.message.add_reaction(self.done_emoji)

    if ctx.message.channel.id == self.commands_channel.id:
      await self.commands_channel.send(output, reference=ctx.message)
    else:
      await self.commands_channel.send(f'{ctx.author.mention}, {output}')

  @_role.error
  async def _role_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      return await ctx.message.add_reaction('⏲️')

    await ctx.message.add_reaction(self.error_emoji)

    if isinstance(error, commands.BadArgument):
      output = 'esse cargo ou não existe, ou não é público.\n*please, check your spelling*.'
      if ctx.message.channel.id == self.commands_channel.id:
        await self.commands_channel.send(output, reference=ctx.message)
      else:
        await self.commands_channel.send(f'{ctx.author.mention}, {output}')

  @commands.command(name='dicinf', aliases=['di', 'dicinformal'])
  @commands.cooldown(2, 60.0, commands.BucketType.user)
  async def _dicionarioinformal(self, ctx, *, term):
    """
    Looks a word up in the Dicionário Informal.

    Don't trust this dictionary blindly. It's like a Brazilian Urban Dictionary.
    """
    def _meaning(entry):
      result = dicinformal.Query(entry)
      embed = discord.Embed(
          title=result.term,
          url=result.url,
          description=f'||{result.description}||',
          color=0x3498DB
      )
      embed.set_footer(icon_url=result.favicon, text=result.disclaimer)
      return embed

    await self.commands_channel.send(ctx.author.mention, embed=_meaning(term))

  @_dicionarioinformal.error
  async def _dicionarioinformal_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      return await ctx.message.add_reaction('⏲️')

    await ctx.message.add_reaction(self.error_emoji)

  @commands.command(name='priberam', aliases=['pri'])
  @commands.cooldown(2, 60.0, commands.BucketType.user)
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

    await self.commands_channel.send(ctx.author.mention + '\n' + output)

  @_priberam.error
  async def _priberam_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      return await ctx.message.add_reaction('⏲️')

    await ctx.message.add_reaction(self.error_emoji)

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
  @commands.cooldown(2, 60.0, commands.BucketType.user)
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
        description=f'||{definition}||',
        color=0x3498DB
    )
    embed.set_footer(icon_url=query.favicon, text=query.disclaimer)

    await self.commands_channel.send(ctx.author.mention, embed=embed)

  @_urbandictionary.error
  async def _urbandictionary_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      return await ctx.message.add_reaction('⏲️')

    await ctx.message.add_reaction(self.error_emoji)

  def to_source(arg):
    source_dicts = {
        'dicio': ['d', 'di', 'dic'],
        'priberam': ['p', 'pr', 'pri'],
    }
    inv_source_dicts = {v: k for k, vs in source_dicts.items() for v in vs}
    return inv_source_dicts[arg.lower()]

  @commands.command(
      aliases=['definição', 'defina', 'definicao', 'definition', 'def', 'd']
  )
  @commands.cooldown(3, 60.0, commands.BucketType.user)
  async def define(
      self,
      ctx,
      src_dict: Optional[to_source] = 'dicio',
      def_num: Optional[int] = 1,
      ent_num: Optional[int] = 1,
      *,
      qry_term = 'nada'
  ):
    """
    Finds a word definition from online dictionaries.

    Supported dictionaries:
    - Dicio (`>define [d | di | dic]`)
    - Priberam (`>define [p | pr | pri]`) 
    """
    if src_dict == 'dicio':
      src_icon = 'https://i.imgur.com/VaE8x5G.png'
      src_name = 'Dicio'
      result = ds.dicio(qry_term)
    else:
      src_icon = 'https://i.imgur.com/Uj6eUTh.png'
      src_name = 'Priberam'
      result = ds.priberam(qry_term)

    if result is None or len(result.entries) == 0:
      raise commands.BadArgument

    await ctx.message.add_reaction(self.done_emoji)

    num_ents = len(result.entries)
    ent_idx = max(1, min(num_ents, ent_num))

    entry = result.entries[ent_idx - 1]

    terms = ' | '.join([f':flag_{k}: {v}' for k, v in entry.terms.items()])

    all_defs = entry.definitions.values()
    defs = [d for ds in all_defs for d in ds]

    num_defs = len(defs)
    def_idx = max(1, min(num_defs, def_num))

    embed = discord.Embed(
        title=result.query,
        url=result.source,
        description=terms + ' ⇒ ' + defs[def_idx - 1],
        color=0x3498DB
    )
    embed.set_footer(
        text=f'entrada {ent_idx}/{num_ents}, definição {def_idx}/{num_defs}',
        icon_url=src_icon
    )

    await ctx.send(
        f'Definição de “{result.query}” no {src_name}:', embed=embed, reference=ctx.message
    )

  @define.error
  async def define_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      return await ctx.message.add_reaction('⏲️')

    await ctx.message.add_reaction(self.error_emoji)


def setup(bot):
  bot.add_cog(Utilities(bot))
