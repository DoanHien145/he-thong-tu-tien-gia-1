import os
import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

async def check_is_owner_or_admin(interaction: discord.Interaction) -> bool:
    if await interaction.client.is_owner(interaction.user):
        return True
    if interaction.guild and interaction.user.id == interaction.guild.owner_id:
        return True
    if isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator:
        return True
    return False

async def check_is_server_owner_or_bot_owner(interaction: discord.Interaction) -> bool:
    if await interaction.client.is_owner(interaction.user):
        return True
    if interaction.guild and interaction.user.id == interaction.guild.owner_id:
        return True
    return False

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cong_exp", description="[Owner] Cộng hoặc trừ EXP tu vi cho đệ tử (Chủ Server / Owner)")
    @app_commands.describe(user="Đệ tử nhận EXP", exp_amount="Số lượng EXP (+ hoặc -)")
    async def cong_exp(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        exp_amount: int
    ):
        if not await check_is_server_owner_or_bot_owner(interaction):
            await interaction.response.send_message("❌ Lệnh này dành riêng cho Chủ Server Discord (Server Owner) / Bot Owner!", ephemeral=True)
            return

        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        updated, _ = await self.bot.excel_manager.add_exp(target_id, exp_amount)
        await self.bot.excel_manager.save()

        embed = discord.Embed(
            title="🛠️ Tông Môn Ban Thưởng EXP (Owner)",
            description=(
                f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã điều chỉnh EXP cho **{target_name}**:\n\n"
                f"⚡ Thay đổi: **{exp_amount:+} EXP**\n"
                f"📈 Tổng EXP hiện tại: `{updated.get('EXP'):,}` EXP"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /cong_exp {exp_amount} for {target_name} by Owner {interaction.user.display_name}")

    @app_commands.command(name="give_exp", description="[Owner] Lệnh give EXP dành riêng cho Chủ Server / Owner")
    @app_commands.describe(user="Đệ tử nhận EXP", amount="Số lượng EXP ban phát")
    async def give_exp(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: int
    ):
        await self.cong_exp(interaction, user, amount)

    @app_commands.command(name="cong_linh_thach", description="[Owner] Cộng hoặc trừ Linh Thạch cho đệ tử (Chủ Server / Owner)")
    @app_commands.describe(user="Đệ tử nhận Linh Thạch", amount="Số lượng Linh Thạch (+ hoặc -)")
    async def cong_linh_thach(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: int
    ):
        if not await check_is_server_owner_or_bot_owner(interaction):
            await interaction.response.send_message("❌ Lệnh này dành riêng cho Chủ Server Discord (Server Owner) / Bot Owner!", ephemeral=True)
            return

        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        updated = await self.bot.excel_manager.add_linh_thach(target_id, amount)
        await self.bot.excel_manager.save()

        embed = discord.Embed(
            title="🛠️ Ban Phát Linh Thạch (Owner)",
            description=(
                f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã điều chỉnh Linh Thạch cho **{target_name}**:\n\n"
                f"💎 Thay đổi: **{amount:+} Linh Thạch** 💎\n"
                f"💰 Tổng Linh Thạch: `{updated.get('Linh thạch'):,}` LT"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /cong_linh_thach {amount} for {target_name} by Owner {interaction.user.display_name}")

    @app_commands.command(name="give_linh_thach", description="[Owner] Lệnh give Linh Thạch dành riêng cho Chủ Server / Owner")
    @app_commands.describe(user="Đệ tử nhận Linh Thạch", amount="Số lượng Linh Thạch ban phát")
    async def give_linh_thach(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: int
    ):
        await self.cong_linh_thach(interaction, user, amount)

    @app_commands.command(name="give", description="[Owner] Lệnh ban phát EXP, Linh Thạch, hoặc Vật Phẩm cho đệ tử (Chủ Server / Owner)")
    @app_commands.describe(
        user="Đệ tử nhận thưởng",
        loai="Loại phần thưởng: EXP, Linh Thạch, hoặc Vật Phẩm",
        so_luong="Số lượng EXP / Linh Thạch / Vật phẩm",
        ten_vat_pham="Tên vật phẩm (chỉ cần khi chọn loại Vật Phẩm)"
    )
    @app_commands.choices(loai=[
        app_commands.Choice(name="✨ EXP Tu vi", value="exp"),
        app_commands.Choice(name="💎 Linh Thạch", value="linh_thach"),
        app_commands.Choice(name="📦 Vật Phẩm / Đan Dược", value="vat_pham")
    ])
    async def give(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        loai: str,
        so_luong: int,
        ten_vat_pham: str = None
    ):
        if not await check_is_server_owner_or_bot_owner(interaction):
            await interaction.response.send_message("❌ Lệnh này dành riêng cho Chủ Server Discord (Server Owner) / Bot Owner!", ephemeral=True)
            return

        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        if so_luong <= 0:
            await interaction.response.send_message("❌ Số lượng ban phát phải lớn hơn 0!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name
        await self.bot.excel_manager.get_or_create_player(target_id, target_name)

        if loai == "exp":
            updated, _ = await self.bot.excel_manager.add_exp(target_id, so_luong)
            await self.bot.excel_manager.save()
            embed = discord.Embed(
                title="🎁 BAN PHÁT EXP TU VI (OWNER GIVE)",
                description=(
                    f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã ban phát **+{so_luong:,} EXP** tu vi cho **{target_name}**!\n\n"
                    f"📈 EXP Tu vi hiện tại: `{updated.get('EXP'):,}` EXP"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)

        elif loai == "linh_thach":
            updated = await self.bot.excel_manager.add_linh_thach(target_id, so_luong)
            await self.bot.excel_manager.save()
            embed = discord.Embed(
                title="🎁 BAN PHÁT LINH THẠCH (OWNER GIVE)",
                description=(
                    f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã ban phát **+{so_luong:,} Linh Thạch** 💎 cho **{target_name}**!\n\n"
                    f"💰 Linh Thạch hiện tại: `{updated.get('Linh thạch'):,}` LT"
                ),
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed)

        elif loai == "vat_pham":
            if not ten_vat_pham:
                await interaction.response.send_message("❌ Bạn chưa nhập tên vật phẩm cần ban phát!", ephemeral=True)
                return
            item_name = ten_vat_pham.strip()
            new_inv = await self.bot.excel_manager.add_item(target_id, item_name, so_luong)
            current_qty = new_inv.get(item_name, 0)
            await self.bot.excel_manager.save()
            embed = discord.Embed(
                title="🎁 BAN PHÁT VẬT PHẨM (OWNER GIVE)",
                description=(
                    f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã ban phát **{so_luong:,}x {item_name}** cho **{target_name}**!\n\n"
                    f"🎒 Số lượng trong Túi Đồ đệ tử: `{current_qty:,}` món"
                ),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)

    @give.autocomplete("ten_vat_pham")
    async def give_vat_pham_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        items = [
            "Luyện Khí Đan", "Tụ Khí Đan", "Thanh Tâm Đan", "Ngưng Nguyệt Đan", "Hồi Xuân Đan",
            "Trúc Cơ Đan", "Tẩy Tủy Đan", "Thần Hành Đan", "Cốt Sủy Đan", "Tụ Linh Đan",
            "Kim Đan Bảo Đan", "Ngũ Hành Linh Đan", "Địa Mẫu Đan", "Nguyên Anh Đan", "Chân Long Đan",
            "Phượng Hoàng Niết Bàn Đan", "Hóa Thần Đan", "Thái Sơ Hóa Đan",
            "Tam Diệp Thảo", "U Nhược Hoa", "Bích Ngọc Liên", "Cửu Diệp Nguyệt Thảo", "Xích Viêm Quả",
            "Lôi Linh Quả", "Vạn Năm Linh Chi", "Hóa Cốt Thảo", "Ngũ Hành Quả", "Địa Mẫu Tinh Tủy",
            "Thiên Niên Tuyết Liên", "Long Dược Căn", "Phượng Hoàng Hoa", "Hóa Thần Thảo", "Thái Sơ Linh Chi"
        ]
        matches = [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()
        ]
        return matches[:25]

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
        await self.bot.excel_manager.save()

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

    @app_commands.command(name="cap_nhat_onedrive", description="[Admin/Owner] Tự động tải và đồng bộ dữ liệu mới nhất từ OneDrive về SQLite")
    @app_commands.describe(link_onedrive="Link chia sẻ OneDrive (Tùy chọn, nếu không nhập sẽ dùng link mặc định)")
    @app_commands.checks.has_permissions(administrator=True)
    async def cap_nhat_onedrive(
        self,
        interaction: discord.Interaction,
        link_onedrive: str = None
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            from bot.import_onedrive import download_and_import_onedrive
            import asyncio
            url_to_use = link_onedrive.strip() if link_onedrive else None
            players_count, items_count = await asyncio.to_thread(download_and_import_onedrive, url_to_use) if url_to_use else await asyncio.to_thread(download_and_import_onedrive)

            # Reload database and save to Excel
            await self.bot.excel_manager.save()

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

    @app_commands.command(name="gift", description="[Owner/Admin] Ban phát vật phẩm với số lượng tùy chọn cho đệ tử")
    @app_commands.describe(user="Đệ tử nhận quà", vat_pham="Tên vật phẩm ban phát", so_luong="Số lượng vật phẩm (Mặc định: 1)")
    async def gift(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        vat_pham: str,
        so_luong: int = 1
    ):
        if not await check_is_owner_or_admin(interaction):
            await interaction.response.send_message("❌ Ngươi không có quyền Chưởng Môn / Owner để dùng lệnh này!", ephemeral=True)
            return

        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        if so_luong <= 0:
            await interaction.response.send_message("❌ Số lượng vật phẩm phải lớn hơn 0!", ephemeral=True)
            return

        target_id = str(user.id)
        target_name = user.display_name
        item_name = vat_pham.strip()

        player = await self.bot.excel_manager.get_or_create_player(target_id, target_name)
        new_inv = await self.bot.excel_manager.add_item(target_id, item_name, so_luong)
        current_qty = new_inv.get(item_name, 0)
        await self.bot.excel_manager.save()

        embed = discord.Embed(
            title="🎁 TÔNG MÔN BAN THƯỞNG VẬT PHẨM (OWNER)",
            description=(
                f"✨ **Chưởng môn / Owner {interaction.user.display_name}** đã ban phát vật phẩm cho **{target_name}**:\n\n"
                f"📦 **Vật phẩm**: **{so_luong:,}x {item_name}**\n"
                f"🎒 **Tổng số lượng trong Túi Đồ**: `{current_qty:,}` món\n\n"
                f"🔒 *Vật phẩm đã được cất trực tiếp vào Túi Đồ của đệ tử.*"
            ),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Command Executed: /gift {so_luong}x '{item_name}' for {target_name} by {interaction.user.display_name}")

    @gift.autocomplete("vat_pham")
    async def gift_vat_pham_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        items = [
            "Luyện Khí Đan", "Tụ Khí Đan", "Thanh Tâm Đan", "Ngưng Nguyệt Đan", "Hồi Xuân Đan",
            "Trúc Cơ Đan", "Tẩy Tủy Đan", "Thần Hành Đan", "Cốt Sủy Đan", "Tụ Linh Đan",
            "Kim Đan Bảo Đan", "Ngũ Hành Linh Đan", "Địa Mẫu Đan", "Nguyên Anh Đan", "Chân Long Đan",
            "Phượng Hoàng Niết Bàn Đan", "Hóa Thần Đan", "Thái Sơ Hóa Đan",
            "Tam Diệp Thảo", "U Nhược Hoa", "Bích Ngọc Liên", "Cửu Diệp Nguyệt Thảo", "Xích Viêm Quả",
            "Lôi Linh Quả", "Vạn Năm Linh Chi", "Hóa Cốt Thảo", "Ngũ Hành Quả", "Địa Mẫu Tinh Tủy",
            "Thiên Niên Tuyết Liên", "Long Dược Căn", "Phượng Hoàng Hoa", "Hóa Thần Thảo", "Thái Sơ Linh Chi"
        ]
        matches = [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()
        ]
        return matches[:25]

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
