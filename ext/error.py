from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord import Embed
from discord.ext import commands
from typing_extensions import Self

from utils import BlacklistedError, MaintenanceError

if TYPE_CHECKING:
    from bot import AloneBot
    from utils import AloneContext


class Error(commands.Cog):
    def __init__(self: Self, bot: AloneBot) -> None:
        self.bot: AloneBot = bot

    @commands.Cog.listener()
    async def on_command_error(self: Self, ctx: AloneContext, error: Exception) -> None:
        "The error handler for the bot."
        if isinstance(error, commands.CommandNotFound):
            return

        await ctx.message.add_reaction(ctx.Emojis.x)
        if isinstance(error, BlacklistedError):
            reason: str | None = self.bot.blacklisted_users.get(ctx.author.id)
            await ctx.reply(
                f"You have been blacklisted for {reason}. you may not appeal this blacklist. There still exists a chance I'll unban you, but it's not likely."
            )

        elif isinstance(error, MaintenanceError):
            await ctx.reply(
                f"The bot is currently in maintenance mode for {self.bot.maintenance}, please wait. If you have any issues, you can join my support server for help."
            )

        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(
                embed=Embed(
                    title="Error",
                    description="You do not have permission to run this command!",
                    color=0xF02E2E,
                )
            )

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"You are on cooldown. Try again in {error.retry_after:.2f}s")

        else:
            channel: Any = self.bot.get_log_channel()
            if ctx.guild:
                guild: str = f"Guild ID: {ctx.guild.id}\n"
            else:
                guild: str = ""
            self.bot.logger.error("An error occurred", exc_info=error)
            embed: Embed = Embed(
                title=f"Ignoring exception in {ctx.command}:",
                description=f"```py\n{error}```\nThe developers have receieved this error and will fix it.",
                color=0xF02E2E,
            )
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.add_field(
                name="Information",
                value=f"Error Name: {type(error).__name__}\nError Type: {type(error)}\nMessage: {ctx.message.content}\n{guild}Channel ID: {ctx.channel.id}",
            )

            await channel.send(
                f"This error came from {ctx.author} using {ctx.command} in {ctx.guild}.",
                embed=embed,
            )
            await ctx.reply(embed=embed)


async def setup(bot: AloneBot) -> None:
    await bot.add_cog(Error(bot))
