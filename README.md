# Zeca

Zeca is a Discord bot for the [Portuguese Learning and Discussion](https://discord.gg/xMwmBZe) server.

## Creating a bot

1. Go to https://discordapp.com/developers/applications/me;
2. Click New App;
3. Enter a name for your bot (and a description) and click *Create App*;
4. Scroll down and click *Create a Bot User*;
5. Click *Save changes*;
6. Under *Bot* click *click to reveal* to show your Token. Copy it and save it somewhere safe\*;

\* Don't let anyone see your token or they will be able to access your bot.

## Adding the bot to your server

1. On the same page click *Generate OAuth2 URL*;
2. Under *Bot Permissions* select *Administrator*;
3. Copy the link and paste it on your browser;
4. Select the server you want to join the bot and click Authorize.

Your bot should now appear on your server.

## Installation

1. Download and install *Python 3.6* and the bot files;
2. If you have Git installed, on the root folder, run ```pip install -r requirements.txt```

    Or if you prefer manual installation:

    ```pip install discord.py```

    ```pip install bs4```

    ```pip install requests```

3. Finally, copy the file `private.py.example` as `private.py` and replace the token value with your newly generated token.
