Exalted Dice Roller for Discord
---

A discord bot for rolling exalted dice, branching off of [@Shalkith's repo](https://github.com/Shalkith/discord_exalted_die_roller "Shalkith/discord_exalted_die_roller")

Setup
---

install via pip:
```bash
$ pip install -r requirements.txt
```

Then make a copy of `.env-TEMPLATE` and copy-paste your Discord Bot token into there
```bash
$ cp .env-TEMPLATE .env
$ sed -i 's/SOME_DISCORD_TOKEN/[..your discord token..]/' .env
```

or simply
```bash
$ echo 'DISCORD_TOKEN=SOME_DISCORD_TOKEN' > .env
```

For information on how to generate a discord bot token and invite your bot to your channel, see [Creating a Bot Account](https://discordpy.readthedocs.io/en/latest/discord.html "discordpy.readthedocs.io")

Developing
---
a `docker-compose.yml` file is provided for local dev so that you can run the main script without a python installation.

With [Watchdog](https://github.com/gorakhargosh/watchdog "gorakhargosh/watchdog") you can run the following command to restart the container automatically upon saving for pseudo-live dev, Angular style. (I'm not skilled enough at Python Thrads to restart the discord server the cool way)
```
$ watchmedo shell-command \
    --patterns="*.py;*.txt" \
    --recursive \
    --command='docker restart discord_exalted_die_roller_roller-bot_1' \
```