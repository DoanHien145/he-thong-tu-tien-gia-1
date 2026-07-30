import random
import time
import discord
from discord import app_commands
from discord.ext import commands
from bot.config import REALMS
from bot.logger import logger
from bot.commands.economy import record_activity

class CultivationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns: dict[str, float] = {}

    @app_commands.command(name="tu_luyen", description="Tiến hành bế quan tu luyện để nhận EXP ngẫu nhiên (Hồi chiêu 20s)")
    async def tu_luyen(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        # Cooldown check (20 seconds)
        now = time.time()
        last_time = self.cooldowns.get(discord_id, 0)
        cooldown_sec = 20
        if now - last_time < cooldown_sec:
            remaining = int(cooldown_sec - (now - last_time))
            await interaction.response.send_message(
                f"⏳ **{username}** đang vận chuyển đại chu thiên, công lực chưa hồi phục!\n"
                f"Vui lòng đợi **{remaining} giây** nữa mới có thể tiếp tục tu luyện.",
                ephemeral=True
            )
            return

        self.cooldowns[discord_id] = now

        # Record activity for quests
        record_activity(discord_id, "tu_luyen")

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)

        # Gain random EXP between 30 and 80
        exp_gain = random.randint(30, 80)
        updated_player, _ = await self.bot.excel_manager.add_exp(discord_id, exp_gain)

        current_realm = updated_player.get("Cảnh giới")
        total_exp = updated_player.get("EXP")

        # Check if enough to breakthrough
        realm_names = [r["name"] for r in REALMS]
        breakthrough_hint = ""
        if current_realm in realm_names:
            idx = realm_names.index(current_realm)
            req_exp = REALMS[idx]["exp_required"]
            if total_exp >= req_exp:
                breakthrough_hint = "\n⚡ *Căn cơ đã đầy đủ, ngươi có thể dùng lệnh `/dot_pha` để đột phá ngay!*"

        embed = discord.Embed(
            title="🧘‍♂️ Bế Quan Tu Luyện",
            description=(
                f"**{updated_player.get('Tên')}** hấp thụ linh khí thiên địa...\n"
                f"✨ Nhận được **+{exp_gain} EXP**!\n"
                f"Tổng EXP hiện tại: `{total_exp}` EXP\n"
                f"Cảnh giới hiện tại: **{current_realm}**"
                f"{breakthrough_hint}"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /tu_luyen by {username} (+{exp_gain} EXP)")

    @app_commands.command(name="dot_pha", description="Thử đột phá cảnh giới khi đạt đủ EXP")
    async def dot_pha(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_realm = player.get("Cảnh giới", "Luyện Khí tầng 1")
        current_exp = int(player.get("EXP", 0))

        realm_names = [r["name"] for r in REALMS]
        if current_realm not in realm_names:
            # Fallback if unknown
            idx = 0
        else:
            idx = realm_names.index(current_realm)

        if idx >= len(REALMS) - 1:
            embed = discord.Embed(
                title="🌌 Đột Phá Cảnh Giới",
                description=f"**{player.get('Tên')}** đã đạt cảnh giới tối cao **{current_realm}**! Không thể đột phá thêm.",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
            return

        req_exp = REALMS[idx]["exp_required"]
        next_realm = REALMS[idx + 1]["name"]

        buff_val = int(player.get("Buff đột phá", 0))
        buff_notice = f"\n⚡ *Đã kích hoạt Buff Đột Phát dược lực: +{buff_val}% cơ duyên!*" if buff_val > 0 else ""

        if current_exp >= req_exp:
            record_activity(discord_id, "dot_pha")
            # Advance realm
            updated = await self.bot.excel_manager.update_player(discord_id, {
                "Cảnh giới": next_realm,
                "Buff đột phá": 0 # Reset consumed buff
            })

            embed = discord.Embed(
                title="⚡ ĐỘT PHÁ THÀNH CÔNG! ⚡",
                description=(
                    f"🎉 Chúc mừng tu sĩ **{player.get('Tên')}** đã giáng hạ thiên kiếp, đột phá thành công!\n\n"
                    f"**{current_realm}**  ➔  **{next_realm}**\n\n"
                    f"✨ EXP hiện tại: `{current_exp}`"
                    f"{buff_notice}"
                ),
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"Command Executed: /dot_pha breakthrough success for {username} to {next_realm}")
        else:
            missing_exp = req_exp - current_exp
            embed = discord.Embed(
                title="🚫 Chưa Thể Đột Phá",
                description=(
                    f"Căn cơ của **{player.get('Tên')}** chưa vững chắc!\n\n"
                    f"☯ Cảnh giới: **{current_realm}**\n"
                    f"✨ EXP hiện tại: `{current_exp}` / `{req_exp}`\n"
                    f"❌ Còn thiếu: **{missing_exp} EXP** nữa để lên **{next_realm}**.\n\n"
                    f"💡 Hãy tiếp tục dùng `/tu_luyen` để tích lũy thêm EXP."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"Command Executed: /dot_pha attempted by {username} (Missing {missing_exp} EXP)")

    @app_commands.command(name="diem_danh", description="Điểm danh hằng ngày để nhận 100 Linh Thạch")
    async def diem_danh(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        # Record activity for quests
        record_activity(discord_id, "diem_danh")

        # Get or create player first
        await self.bot.excel_manager.get_or_create_player(discord_id, username)

        success, player, msg = await self.bot.excel_manager.check_in(discord_id)

        if success:
            embed = discord.Embed(
                title="🎁 Điểm Danh Tông Môn",
                description=(
                    f"**{player.get('Tên')}** đã điểm danh hôm nay!\n\n"
                    f"{msg}\n"
                    f"💎 Linh Thạch hiện tại: **{player.get('Linh thạch')}**"
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⏳ Điểm Danh Tông Môn",
                description=f"**{player.get('Tên')}**: {msg}",
                color=discord.Color.orange()
            )

        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /diem_danh by {username} (Result: {success})")

async def setup(bot):
    await bot.add_cog(CultivationCog(bot))
