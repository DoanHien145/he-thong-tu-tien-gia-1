import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="thongtin", description="Xem thông tin chi tiết nhân vật tu tiên của bạn")
    async def thongtin(self, interaction: discord.Interaction):
        # Channel lock check
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)

        embed = discord.Embed(
            title=f"📜 Hồ Sơ Tu Sĩ — {player.get('Tên')}",
            color=discord.Color.from_rgb(0, 204, 153) # Jade Green xianxia theme
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
        embed.add_field(name="👤 Tu Sĩ", value=f"**{player.get('Tên')}**", inline=True)
        embed.add_field(name="☯ Cảnh Giới", value=f"**{player.get('Cảnh giới')}**", inline=True)
        embed.add_field(name="✨ EXP Tu Vi", value=f"`{player.get('EXP')}` EXP", inline=True)
        embed.add_field(name="💎 Linh Thạch", value=f"`{player.get('Linh thạch')}` 💎", inline=True)
        embed.add_field(name="🌿 Linh Căn", value=f"**{player.get('Linh căn')}**", inline=True)
        embed.add_field(name="❤️ Sinh Lực / Mana", value=f"HP: `{player.get('HP')}` | MP: `{player.get('Mana')}`", inline=True)
        
        last_checkin = player.get("Ngày điểm danh") or "Chưa điểm danh"
        embed.add_field(name="📅 Điểm Danh Gần Nhất", value=f"`{last_checkin}`", inline=False)
        embed.set_footer(text="Tông Môn Đại Lão Ẩn Mình • Dữ liệu lưu trong Excel")

        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /thongtin by {username}")

    @app_commands.command(name="linhthach", description="Xem số lượng Linh Thạch hiện có")
    async def linhthach(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        lt = player.get("Linh thạch", 0)

        embed = discord.Embed(
            title="💎 Túi Linh Thạch Tông Môn",
            description=f"Tu sĩ **{player.get('Tên')}** hiện đang sở hữu **{lt}** Linh Thạch.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /linhthach by {username}")

    @app_commands.command(name="top", description="Xem bảng xếp hạng các tu sĩ mạnh nhất tông môn")
    async def top(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        top_players = await self.bot.excel_manager.get_top_cultivators(limit=10)

        embed = discord.Embed(
            title="🏆 BẢNG VÀNG CẢNH GIỚI TÔNG MÔN",
            description="Danh sách Top 10 đệ tử có tu vi cao nhất tông môn:",
            color=discord.Color.from_rgb(212, 175, 55) # Gold
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for idx, p in enumerate(top_players):
            medal = medals[idx] if idx < len(medals) else "🔹"
            embed.add_field(
                name=f"{medal} #{idx+1} {p.get('Tên')}",
                value=f"☯ **{p.get('Cảnh giới')}** | ✨ `{p.get('EXP')}` EXP | 💎 `{p.get('Linh thạch')}` LT",
                inline=False
            )

        embed.set_footer(text="Hãy siêng năng tu luyện để ghi tên trên Bảng Vàng!")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /top by {interaction.user.display_name}")

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
