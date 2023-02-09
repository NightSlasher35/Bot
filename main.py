import os
from asyncio import run

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

import utils.bot as _bot

load_dotenv()

bot = _bot.AloneBot(intents=Intents.all())


@bot.after_invoke
async def command_counter(ctx: AloneContext):
    bot.command_counter += 1


@bot.check_once
async def blacklist(ctx: AloneContext):
    if not bot.is_blacklisted(ctx.author.id):
        return True
    if ctx.author.id in bot.owner_ids:
        return True
    raise _bot.BlacklistedError


@bot.check_once
async def maintenance(ctx: AloneContext):
    if not bot.maintenance or ctx.author.id in bot.owner_ids:
        return True
    raise _bot.MaintenanceError


async def main():
    async with bot:
        await bot.start(os.environ["token"])


if __name__ == "__main__":
    run(main())
