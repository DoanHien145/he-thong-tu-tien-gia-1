import os
import sys
import asyncio
import discord
from discord.ext import commands

# Ensure python path includes project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.config import DISCORD_TOKEN, CHANNEL_ID, GUILD_ID, EXCEL_PATH
from bot.logger import logger
from bot.excel_manager import ExcelManager
from bot.ai_handler import AIHandler

class TongMonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.excel_manager = ExcelManager(EXCEL_PATH)
        self.ai_handler = AIHandler()
        self.channel_id = CHANNEL_ID
        self.guild_id = GUILD_ID

    async def setup_hook(self):
        """Loads all extension cogs and syncs slash command tree."""
        cogs = [
            "bot.commands.info",
            "bot.commands.cultivation",
            "bot.commands.economy",
            "bot.commands.alchemy",
            "bot.commands.events",
            "bot.commands.admin",
            "bot.commands.help"
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded Cog extension: {cog}")
            except Exception as e:
                logger.error(f"Error loading cog {cog}: {e}")

        # Sync Slash Commands
        try:
            if self.guild_id:
                guild_obj = discord.Object(id=self.guild_id)
                self.tree.copy_global_to(guild=guild_obj)
                synced = await self.tree.sync(guild=guild_obj)
                logger.info(f"Slash Commands Synced to Guild {self.guild_id}: {len(synced)} commands.")
            else:
                synced = await self.tree.sync()
                logger.info(f"Slash Commands Synced Globally: {len(synced)} commands.")
        except Exception as e:
            logger.error(f"Error syncing slash commands: {e}")

    async def on_ready(self):
        logger.info(f"Bot Started: Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"User Login: Active in Guild ID={self.guild_id or 'Global'}, Restricted Channel ID={self.channel_id}")
        logger.info("Tông Môn Đại Lão Bot is ready to serve disciples!")

        # Ensure instant slash command availability in all joined guilds
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} slash commands instantly to guild: {guild.name} (ID: {guild.id})")
            except Exception as e:
                logger.error(f"Error syncing commands to guild {guild.id}: {e}")

        # Set presence
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="kinh văn Tông Môn | /help"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_guild_join(self, guild: discord.Guild):
        """Automatically sync slash commands when joining a new server."""
        try:
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"On Guild Join: Synced {len(synced)} slash commands to new guild {guild.name} (ID: {guild.id})")
        except Exception as e:
            logger.error(f"Error syncing slash commands on guild join ({guild.id}): {e}")

    async def on_message(self, message: discord.Message):
        """
        Enforces single-channel restriction and processes AI natural language queries.
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # STRICT SINGLE-CHANNEL RESTRICTION
        # If CHANNEL_ID is configured and message is from another channel -> STRICTLY IGNORE
        if self.channel_id and message.channel.id != self.channel_id:
            return

        # Check if user sent a message starting with "." prompt trigger for AI response
        content = message.content.strip()
        if content.startswith("."):
            query = content[1:].strip()
            if query:
                # Trigger typing indicator while querying AI
                async with message.channel.typing():
                    discord_id = str(message.author.id)
                    display_name = message.author.display_name

                    # Auto register if new
                    await self.excel_manager.get_or_create_player(discord_id, display_name)

                    # Fetch all Excel players for context
                    all_players = await self.excel_manager.get_all_players()

                    # Get AI answer
                    ai_reply = await self.ai_handler.answer_question(
                        question=query,
                        user_discord_id=discord_id,
                        user_display_name=display_name,
                        excel_data=all_players
                    )

                    await message.reply(ai_reply, mention_author=True)
                    logger.info(f"AI Handled Query from {display_name}: '{query[:30]}...'")

        await self.process_commands(message)

def main():
    if not DISCORD_TOKEN or DISCORD_TOKEN == "your_discord_bot_token_here":
        logger.error("Error: DISCORD_TOKEN is missing or default placeholder! Please set DISCORD_TOKEN in .env or environment variables.")
        print("\n========================================================")
        print("⚠️ DISCORD_TOKEN chưa được cấu hình!")
        print("Vui lòng thiết lập DISCORD_TOKEN trong file .env hoặc biến môi trường Railway.")
        print("========================================================\n")
        return

    bot = TongMonBot()
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error starting Discord Bot: {e}")

if __name__ == "__main__":
    main()
