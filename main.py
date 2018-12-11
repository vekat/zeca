import discord
import private
import os
import sys
import re
import time
from cogs import utilities
from discord.ext import commands

ROOT = os.path.dirname(sys.modules['__main__'].__file__)

command_prefix = '>'
description = """Portuguese Learning and Discussion utilities bot."""

bot = commands.Bot(command_prefix=command_prefix, description=description)

initial_extensions = ['cogs.moderator', 'cogs.utilities', 'cogs.zoeira']

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as ex:
            print('Failed to load extension ' + extension)


# Create blacklist
blacklist = []

# Create name filter
name_filter = re.compile(r'discord\.gg/\S+', re.I)


@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))
    print('Discord Version: {}'.format(discord.__version__))
    print('-------------')
    activity = discord.Game(name='Type >help')
    await bot.change_presence(activity=activity)

    # Removes the hitmeup role from everyone who has it
    guild = bot.guilds[0]
    role = discord.utils.get(guild.roles, name='hitmeup')
    try:
        for member in role.members or []:
            await member.remove_roles(role)
            await member.send(utilities.Utilities.expired_role_msg)
    except AttributeError:
        pass  # Ignores this if no one has the hitmeup role

    # Load blacklisted users
    try:
        with open(os.path.join(ROOT, 'blacklist.txt')) as f:
            blacklist = f.readlines()
            blacklist = [i.strip() for i in blacklist]
            blacklist = [int(i) for i in blacklist]
            print('Blacklisted IDs: ')
            print(blacklist)
    except FileNotFoundError:
        with open(os.path.join(ROOT, 'blacklist.txt'), 'w') as f:
            pass


# Check if user is not blacklisted
@bot.check
def check_user(ctx):
    try:
        with open(os.path.join(ROOT, 'blacklist.txt')) as f:
            blacklist = f.readlines()
            blacklist = [i.strip() for i in blacklist]
            blacklist = [int(i) for i in blacklist]
    except FileNotFoundError:
        pass
    return ctx.author.id not in blacklist


@bot.event
async def on_member_join(member):
    mid = member.id
    guild = member.guild

    general_channel = discord.utils.get(
        bot.get_all_channels(), name='comandos')
    info_channel = discord.utils.get(bot.get_all_channels(), name='regras')

    member_name = str(member)
    if name_filter.findall(member_name):
        return await member.ban(reason="[zeca] banned for blacklisted name")

    time.sleep(10)

    if not guild.get_member(mid):
        return

    welcome_message = 'welcome, ' + member.mention + ' ! ' + \
        'please check out ' + info_channel.mention + ' to learn ' + \
        'about the server rules and cool stuff. :slight_smile:'
    if general_channel is not None:
        await general_channel.send(welcome_message)


@bot.event
async def on_reaction_add(reaction, user):
    print('{}, {}, {}'.format(reaction, user, str(reaction.message.content)))


@bot.command(name='revoke_role', hidden=True)
@commands.is_owner()
async def _revoke_role(ctx, *, role):
    role = await commands.RoleConverter().convert(ctx, role)
    for member in role.members:
        await member.remove_roles(role)
        await member.send(utilities.Utilities.expired_role_msg)


@bot.command(name='eval', hidden=True)
@commands.is_owner()
async def _eval(ctx, *, code):
    """A bad example of an eval command"""
    await ctx.send(eval(code))

bot.run(private.__TOKEN)
