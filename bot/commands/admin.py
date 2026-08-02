import os
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

    @app_commands.command(name="tai_data", description="[Admin/Owner] Tải file cơ sở dữ liệu SQLite (cultivation.db) và Excel (data.xlsx) về máy")
    @app_commands.checks.has_permissions(administrator=True)
    async def tai_data(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Xuất dữ liệu mới nhất từ SQLite ra Excel
        try:
            await self.bot.excel_manager.save()
        except Exception as e:
            logger.error(f"Lỗi khi lưu Excel trước khi gửi: {e}")

        files_to_send = []
        db_path = "data/cultivation.db"
        excel_path = "data/data.xlsx"

        if os.path.exists(db_path):
            files_to_send.append(discord.File(db_path, filename="cultivation.db"))
        if os.path.exists(excel_path):
            files_to_send.append(discord.File(excel_path, filename="data.xlsx"))

        if not files_to_send:
            await interaction.followup.send("❌ Không tìm thấy file dữ liệu nào trên máy chủ!", ephemeral=True)
            return

        embed = discord.Embed(
            title="📦 DỮ LIỆU TÔNG MÔN (Dành cho Chưởng Môn / Owner)",
            description=(
                "Gửi đính kèm các file dữ liệu lưu trữ mới nhất của Tông Môn:\n\n"
                "🗄️ `cultivation.db`: **Cơ sở dữ liệu SQLite** chứa đầy đủ dữ liệu tu sĩ, EXP, Linh Thạch, Túi Đồ v.v.\n"
                "📊 `data.xlsx`: **File bảng tính Excel** tổng hợp thông tin tu sĩ.\n\n"
                "🔒 *Thông tin này được gửi riêng tư (ephemeral) chỉ dành riêng cho bạn.*"
            ),
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed, files=files_to_send, ephemeral=True)
        logger.info(f"Command Executed: /tai_data by {interaction.user.display_name}")

    @app_commands.command(name="cap_nhat_onedrive", description="[Admin] Tự động tải và đồng bộ dữ liệu mới nhất từ OneDrive về SQLite")
    @app_commands.checks.has_permissions(administrator=True)
    async def cap_nhat_onedrive(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            from bot.import_onedrive import download_and_import_onedrive
            import asyncio
            players_count, items_count = await asyncio.to_thread(download_and_import_onedrive)

            embed = discord.Embed(
                title="🔄 CẬP NHẬT DỮ LIỆU ONEDRIVE THÀNH CÔNG!",
                description=(
                    f"✅ **Đã tải và đồng bộ thành công dữ liệu từ OneDrive**!\n\n"
                    f"👥 **Số lượng tu sĩ đồng bộ**: `{players_count}` nhân vật\n"
                    f"🎒 **Số lượng vật phẩm**: `{items_count}` món\n"
                    f"💾 **Cơ sở dữ liệu**: Đã cập nhật vào `cultivation.db` & `data.xlsx`."
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Command Executed: /cap_nhat_onedrive by {interaction.user.display_name}")
        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ OneDrive: {e}")
            await interaction.followup.send(f"❌ Lỗi khi đồng bộ dữ liệu từ OneDrive: {e}", ephemeral=True)

    @cong_exp.error
    @cong_linh_thach.error
    @set_canh_gioi.error
    @tai_data.error
    @cap_nhat_onedrive.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Ngươi không có quyền Chưởng Môn / Admin để dùng lệnh này!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
