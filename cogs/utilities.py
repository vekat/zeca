import discord
import dicinformal
import priberamdict
import asyncio
import re
from discord.ext import commands
from highlighter import compare_texts
from urbandic import UDQuery


class Utilities(commands.Cog):
  """Member utilities."""
  def __init__(self, bot):
    self.bot = bot

  # Some commands variables are class properties, so it's easier
  # to access them from higher levels when needed.
  expired_role_msg = 'your role "hit me up" role has ' + \
                     'expired on the Portuguese server.\nto renew the role, type `>r hitmeup` ' + \
                     'in the <#451912364183257089> channel.\ndon\'t forget this role ' + \
                     'expires in one hour.\nthank you for being part of the ' + \
                     'Portuguese learning and discussion community! :smile:'
  level_roles_aliases = {
      'newbie': ['0', 'a0', 'new'],
      'beginner': ['a', 'a1', 'a2'],
      'intermediate': ['b', 'b1', 'b2'],
      'advanced': ['c', 'c1', 'c2'],
      'native': ['native speaker']
  }

  level_roles = {}

  for k, l in level_roles_aliases.items():
    level_roles[k] = k
    level_roles['level ' + k] = k
    for v in l:
      level_roles[v] = k
      level_roles['level ' + v] = k

  country_roles = {
      'pt': 'PT',
      'br': 'BR',
      'ao': 'AO',
      'cv': 'CV',
      'gq': 'GQ',
      'gw': 'GW',
      'mo': 'MO',
      'mz': 'MZ',
      'st': 'ST',
      'tl': 'TL'
  }
  other_roles = {
      'hitmeup': 'hit me up',
      'hit me up': 'hit me up',
      'notify me': 'notify me',
      'correct me': 'correct me'
  }
  public_roles = {**level_roles, **country_roles, **other_roles}

  @commands.command(name='role', aliases=['r'])
  async def _role(self, ctx, *, role):
    """
        Assigns or removes a role.

        If role is a level role (Level A, Level B, Level C, or Native),
        the previous level will be automatically removed.

        The role 'hit me up' expires after 1 hour.

        Sub-command:
            list:  Shows a list of public roles.
        """

    if role.lower() in list(self.public_roles.keys()):
      role = self.public_roles[role.lower()]
      role = await commands.RoleConverter().convert(ctx, role)
      member = ctx.author
      if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(':white_check_mark: Role removed.')
      else:
        if role.name in list(self.level_roles.values()):
          for _, r in enumerate(member.roles):
            if r.name in list(self.level_roles.values()):
              await member.remove_roles(r)
        await member.add_roles(role)
        await ctx.send(':white_check_mark: Role granted.')
        # Schedules the hitmeup role expiration
        if role.name == 'hit me up':
          await asyncio.sleep(3600)
          if role in member.roles:
            await member.remove_roles(role)
            await ctx.author.send(self.expired_role_msg)

    elif role == 'list':
      output = 'Public roles available:\n' + '```' + \
               ', '.join(
                   list(dict.fromkeys(self.public_roles.values()))) + '```'
      await ctx.send(output)
    else:
      raise commands.BadArgument

  @_role.error
  async def _role_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send(
          ':exclamation:This role does not exist or is not ' +
          'public. Check your spelling.'
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

    def _synonym(entry):
      return 'synonym of {}'.format(entry)

    def _antonym(entry):
      return 'antonym of {}'.format(entry)

    # Parse sub-command
    sub_commands = {'-a': _antonym, '-s': _synonym}
    sub_command = [i for i in term if i in list(sub_commands.keys())]
    if sub_command:
      sub_command = sub_command[0]
      term = list(term)
      term.remove(sub_command)
      term = ' '.join(term)
      await ctx.send(sub_commands[sub_command](term))
    # Default command
    else:
      term = ' '.join(term)
      await ctx.send(embed=_meaning(term))

  @_dicionarioinformal.error
  async def _dicionarioinformal_error(self, ctx, error):
    if isinstance(error, commands.CommandInvokeError):
      # await ctx.send(error.__cause__)
      await ctx.send(':exclamation: No results found.')

  @commands.command(name='priberam', aliases=['pri'])
  async def _priberam(self, ctx, *, entry):
    """ Looks up a word in the Priberam Portuguese dictionary.

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

        await ctx.send(output)

    @_priberam.error
    async def __priberam_error(self, ctx, error):
        await ctx.send(error.__cause__)

    @commands.command()
    async def nick(self, ctx, *, new_nick):
        """ Changes the nickname of a member. """
        member = ctx.author
        await member.edit(nick=new_nick)

    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            # await ctx.send(error.__cause__)
            await ctx.send('I don\'t have permission for that, master.')

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
    await ctx.send(embed=embed)


def setup(bot):
  bot.add_cog(Utilities(bot))
