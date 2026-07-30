import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cong_exp", description="[Admin] Cộng hoặc trừ EXP cho đệ tử")
    @app_commands.checks.has_permissions(administrator=True)
    async def cong_exp(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        exp_amount: int
    ):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        updated, _ = await self.bot.excel_manager.add_exp(target_id, exp_amount)

        embed = discord.Embed(
            title="🛠️ Tông Môn Ban Thưởng (Admin)",
            description=(
                f"Chưởng môn / Admin đã điều chỉnh EXP cho **{target_name}**:\n"
                f"Thay đổi: **{exp_amount:+} EXP**\n"
                f"Tổng EXP hiện tại: `{updated.get('EXP')}`"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /cong_exp {exp_amount} for {target_name} by {interaction.user.display_name}")

    @app_commands.command(name="cong_linh_thach", description="[Admin] Cộng hoặc trừ Linh Thạch cho đệ tử")
    @app_commands.checks.has_permissions(administrator=True)
    async def cong_linh_thach(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: int
    ):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        updated, _ = await self.bot.excel_manager.add_linh_thach(target_id, amount)

        embed = discord.Embed(
            title="🛠️ Ban Phát Linh Thạch (Admin)",
            description=(
                f"Chưởng môn / Admin đã điều chỉnh Linh Thạch cho **{target_name}**:\n"
                f"Thay đổi: **{amount:+} Linh Thạch** 💎\n"
                f"Tổng Linh Thạch: `{updated.get('Linh thạch')}`"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /cong_linh_thach {amount} for {target_name} by {interaction.user.display_name}")

    @app_commands.command(name="set_canh_gioi", description="[Admin] Đổi cảnh giới cho đệ tử")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_canh_gioi(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        canh_gioi_moi: str
    ):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        updated = await self.bot.excel_manager.update_player(target_id, {"Cảnh giới": canh_gioi_moi})

        embed = discord.Embed(
            title="🛠️ Thiết Lập Cảnh Giới (Admin)",
            description=(
                f"Chưởng môn / Admin đã đổi cảnh giới cho **{target_name}** thành:\n"
                f"☯ **{canh_gioi_moi}**"
            ),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /set_canh_gioi '{canh_gioi_moi}' for {target_name} by {interaction.user.display_name}")

    @cong_exp.error
    @cong_linh_thach.error
    @set_canh_gioi.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Ngươi không có quyền Chưởng Môn / Admin để dùng lệnh này!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
