Exalted Dice Roller for Discord
---

A discord bot for rolling exalted dice, branching off of [@Shalkith's repo](https://github.com/Shalkith/discord_exalted_die_roller "Shalkith/discord_exalted_die_roller")

Setup
---

install via pip:
```bash
$ pip install -r requirements.txt
```

or via pipenv:
```bash
$ pipenv install $(cat requirements.txt)
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
