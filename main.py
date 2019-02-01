import discord
import private
import os
import sys
import re
import time
import asyncio
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

    member_name = str(member)
    if name_filter.findall(member_name):
        return await member.ban(reason="[zeca] banned for blacklisted name")

    general_channel = guild.get_channel(private.__welcome)
    rules_channel = guild.get_channel(private.__rules)
    roles_channel = guild.get_channel(private.__roles)
    rooms_channel = guild.get_channel(private.__rooms)

    await asyncio.sleep(private.__delay)

    if not guild.get_member(mid):
        return

    welcome_message = ':flag_gb: welcome ' + member.mention + ' ! :flag_us:\n' + \
        'please use this waiting period to get to know about:\n— our server rules in ' + rules_channel.mention + '\n— our server roles in ' + roles_channel.mention + '\n— our server chats in ' + rooms_channel.mention + '\n\n' + \
        'when you are able to type, send commands here to get yourself a role\n' + \
        '*you need a level role to use the other channels*\n\n' + \
        ':flag_pt: seja bem-vindo(a) ! :flag_br:\n' + \
        'por favor use este tempo para conhecer:\n— nossas regras em ' + rules_channel.mention + '\n— nossos cargos em ' + roles_channel.mention + '\n— nossos canais em ' + rooms_channel.mention + '\n\n' + \
        'assim que puder digitar, envie comandos aqui para receber seus cargos\n' + \
        '*você precisa de um cargo de nível para usar os outros canais*'
    if general_channel:
        await general_channel.send(welcome_message)


bot.run(private.__TOKEN)
