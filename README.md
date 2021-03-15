# Zeca

Zeca is a Discord bot for the [Portuguese Learning and Discussion](https://discord.gg/xMwmBZe) server.

## Creating a bot

1. Go to https://discordapp.com/developers/applications;
2. Click on New Application;
3. Enter a name for your bot and click on *Create*;
4. Click on Bot and then click on Add Bot.
6. Under *Build-A-Bot* click on Copy to copy your token, and save it somewhere safe\*;

\* Don't let anyone see your token or they will be able to access your bot.

## Adding the bot to your server

1. On the same page click *Generate OAuth2 URL*;
2. Under *Scopes* check *bot*;
3. Under *Bot Permissions* check *Administrator*;
4. Copy the link and paste it on your browser;
5. Select the server you want the bot to join and click on Authorize.

Your bot should now appear on your server.

## Installation

1. Download and install *Python 3.8* and the bot files;
2. On the root folder, run ```pip install -r requirements.txt```
3. Finally, copy the file `private.py.example` as `private.py` and replace the token value with your newly generated token.
