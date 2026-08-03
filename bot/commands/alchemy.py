import random
import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger
from bot.commands.economy import record_activity

RECIPES = {
    "Luyện Khí Đan": {
        "ingredients": {"Tam Diệp Thảo": 2},
        "success_rate": 0.85,
        "explosion_rate": 0.05,
        "exp_loss_on_explosion": 30,
        "type": "exp",
        "effect_val": 300,
        "desc": "Linh đan Nhất Phẩm • Thành công 85% • Cắn đan +300 EXP"
    },
    "Tụ Khí Đan": {
        "ingredients": {"Tam Diệp Thảo": 2, "U Nhược Hoa": 1},
        "success_rate": 0.70,
        "explosion_rate": 0.08,
        "exp_loss_on_explosion": 50,
        "type": "buff",
        "effect_val": 20,
        "desc": "Linh đan Nhất Phẩm • Thành công 70% • Buff +20% Đột Phá"
    },
    "Trúc Cơ Đan": {
        "ingredients": {"U Nhược Hoa": 2, "Xích Viêm Quả": 1},
        "success_rate": 0.55,
        "explosion_rate": 0.10,
        "exp_loss_on_explosion": 100,
        "type": "exp",
        "effect_val": 1500,
        "desc": "Linh đan Nhị Phẩm • Thành công 55% • Cắn đan +1500 EXP"
    },
    "Tẩy Tủy Đan": {
        "ingredients": {"Xích Viêm Quả": 2, "Lôi Linh Quả": 1},
        "success_rate": 0.40,
        "explosion_rate": 0.12,
        "exp_loss_on_explosion": 200,
        "type": "buff",
        "effect_val": 35,
        "desc": "Linh đan Nhị Phẩm (Hiếm) • Thành công 40% • Buff +35% Đột Phá"
    },
    "Kim Đan Bảo Đan": {
        "ingredients": {"Lôi Linh Quả": 2, "Vạn Năm Linh Chi": 1},
        "success_rate": 0.30,
        "explosion_rate": 0.15,
        "exp_loss_on_explosion": 500,
        "type": "exp",
        "effect_val": 5000,
        "desc": "Linh đan Tam Phẩm • Thành công 30% • Cắn đan +5000 EXP & Buff +50% Đột phá"
    },
    "Nguyên Anh Đan": {
        "ingredients": {"Vạn Năm Linh Chi": 2, "Thiên Niên Tuyết Liên": 1},
        "success_rate": 0.20,
        "explosion_rate": 0.20,
        "exp_loss_on_explosion": 1000,
        "type": "exp",
        "effect_val": 15000,
        "desc": "Linh đan Tứ Phẩm (Thượng Phẩm) • Thành công 20% • Cắn đan +15,000 EXP"
    },
    "Hồi Xuân Đan": {
        "ingredients": {"Tam Diệp Thảo": 3, "U Nhược Hoa": 1},
        "success_rate": 0.80,
        "explosion_rate": 0.05,
        "exp_loss_on_explosion": 20,
        "type": "heal",
        "effect_val": 100,
        "desc": "Linh đan Phục Hồi • Hồi phục 100 HP & 100 Mana"
    },
    "Thần Hành Đan": {
        "ingredients": {"Xích Viêm Quả": 1, "Vạn Năm Linh Chi": 1},
        "success_rate": 0.50,
        "explosion_rate": 0.10,
        "exp_loss_on_explosion": 150,
        "type": "buff",
        "effect_val": 25,
        "desc": "Linh đan Trợ Chiến • Tăng +25% né tránh tác động lôi kiếp"
    }
}

DAN_EFFECTS = {
    "Luyện Khí Đan": {"type": "exp", "val": 300, "desc": "Tăng +300 EXP tu vi!"},
    "Trúc Cơ Đan": {"type": "exp", "val": 1500, "desc": "Tăng +1500 EXP tu vi!"},
    "Kim Đan Bảo Đan": {"type": "exp_buff", "val": 5000, "buff": 50, "desc": "Tăng +5000 EXP & +50% Buff Đột Phá!"},
    "Nguyên Anh Đan": {"type": "exp", "val": 15000, "desc": "Tăng +15,000 EXP tu vi vĩ đại!"},
    "Tụ Khí Đan": {"type": "buff", "val": 20, "desc": "Gia tăng +20% tỉ lệ thành công cho lần Đột Phá tiếp theo!"},
    "Tẩy Tủy Đan": {"type": "buff", "val": 35, "desc": "Gia tăng +35% tỉ lệ thành công cho lần Đột Phá tiếp theo!"},
    "Thần Hành Đan": {"type": "buff", "val": 25, "desc": "Gia tăng +25% Tỉ lệ Đột Phá chấn áp Tâm Ma!"},
    "Hồi Xuân Đan": {"type": "heal", "val": 100, "desc": "Phục hồi 100 HP & 100 Mana lập tức!"}
}

class AlchemyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tui_do", description="Xem Túi Đồ Linh Đan & Dược Liệu của bạn")
    async def tui_do(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        inventory = await self.bot.excel_manager.get_inventory(discord_id)

        buff = int(player.get("Buff đột phá", 0))

        embed = discord.Embed(
            title=f"🎒 Túi Đồ Tu Tiên — {player.get('Tên')}",
            color=discord.Color.from_rgb(0, 204, 153)
        )

        if buff > 0:
            embed.add_field(
                name="✨ Buff Đột Phá Tích Lũy",
                value=f"⚡ Gia tăng **+{buff}%** tỉ lệ thành công khi dùng `/dot_pha`!",
                inline=False
            )

        if not inventory or all(v <= 0 for v in inventory.values()):
            embed.description = "Túi đồ của bạn hiện đang trống rỗng!\nHãy dùng `/nhiemvu`, `/shop`, `/sukien` để kiếm Linh Đan và Dược Liệu."
        else:
            dan_items = []
            nguyen_lieu_items = []

            for item_name, count in inventory.items():
                if count <= 0:
                    continue
                if "Đan" in item_name:
                    dan_items.append(f"🧪 **{item_name}**: `{count}` viên")
                else:
                    nguyen_lieu_items.append(f"🌿 **{item_name}**: `{count}` cái")

            if dan_items:
                embed.add_field(
                    name="🧪 Linh Đan",
                    value="\n".join(dan_items),
                    inline=False
                )
            if nguyen_lieu_items:
                embed.add_field(
                    name="🌿 Dược Liệu & Nguyên Liệu",
                    value="\n".join(nguyen_lieu_items),
                    inline=False
                )

        embed.set_footer(text="Dùng /che_dan để luyện đan • Dùng /dung_dan [tên_đan] để cắn đan")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="che_dan", description="Luyện chế Linh Đan từ nguyên liệu trong túi đồ")
    @app_commands.describe(ten_dan="Tên loại đan muốn chế (để trống để xem bí kíp công thức)")
    async def che_dan(self, interaction: discord.Interaction, ten_dan: str = ""):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        record_activity(discord_id, "che_dan", self.bot)

        if not ten_dan:
            embed = discord.Embed(
                title="📜 BÍ KÍP LUYỆN ĐAN TÔNG MÔN",
                description="Danh sách công thức chế đan dược & tỉ lệ luyện chế thành công:\nDùng lệnh: `/che_dan [tên_đan]`",
                color=discord.Color.gold()
            )
            for dan_name, recipe in RECIPES.items():
                ing_str = ", ".join([f"`{count}x {ing}`" for ing, count in recipe["ingredients"].items()])
                embed.add_field(
                    name=f"🧪 {dan_name} (Tỉ lệ thành công: {int(recipe['success_rate']*100)}%)",
                    value=f"└ 🌿 Nguyên liệu: {ing_str}\n└ ✨ Tác dụng: {recipe['desc']}",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)
            return

        matched_recipe_name = None
        for recipe_name in RECIPES:
            if ten_dan.strip().lower() in recipe_name.lower():
                matched_recipe_name = recipe_name
                break

        if not matched_recipe_name:
            await interaction.response.send_message(f"❌ Không tìm thấy công thức cho đan **{ten_dan}**. Dùng `/che_dan` để xem danh sách!", ephemeral=True)
            return

        recipe = RECIPES[matched_recipe_name]
        inventory = await self.bot.excel_manager.get_inventory(discord_id)

        missing = []
        for ing, req_count in recipe["ingredients"].items():
            have = inventory.get(ing, 0)
            if have < req_count:
                missing.append(f"• **{ing}**: Thiếu `{req_count - have}` cái (Hiện có `{have}`/`{req_count}`)")

        if missing:
            embed = discord.Embed(
                title="🚫 Thiếu Nguyên Liệu Luyện Đan",
                description=f"Bạn không đủ nguyên liệu chế **{matched_recipe_name}**:\n" + "\n".join(missing) + "\n\nHãy làm `/nhiemvu` hoặc mua ở `/shop`!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Deduct ingredients using use_item
        for ing, req_count in recipe["ingredients"].items():
            await self.bot.excel_manager.use_item(discord_id, ing, req_count)

        is_success = random.random() <= recipe["success_rate"]

        if is_success:
            await self.bot.excel_manager.add_item(discord_id, matched_recipe_name, 1)
            embed = discord.Embed(
                title="🔥 LUYỆN ĐAN THÀNH CÔNG!",
                description=(
                    f"🎉 **{username}** vận chuyển thái cực linh hỏa, khai lò luyện chế thành công **1x {matched_recipe_name}**!\n\n"
                    f"✨ Đan dược đã cất vào Túi Đồ. Dùng `/dung_dan {matched_recipe_name}` để sử dụng ngay!"
                ),
                color=discord.Color.green()
            )
        else:
            is_explosion = random.random() <= recipe.get("explosion_rate", 0.10)
            if is_explosion:
                exp_loss = recipe.get("exp_loss_on_explosion", 50)
                player_data = await self.bot.excel_manager.get_player(discord_id)
                current_exp = int(player_data.get("EXP", 0)) if player_data else 0
                new_exp = max(0, current_exp - exp_loss)
                await self.bot.excel_manager.update_player(discord_id, {"EXP": new_exp})
                updated_player = await self.bot.excel_manager.get_player(discord_id)

                embed = discord.Embed(
                    title="💥 NỔ LÒ LUYỆN ĐAN — TỔN THƯƠNG TU VI!",
                    description=(
                        f"😱 Hỏa lực bộc phát cuồng bạo! Lò luyện đan của **{username}** phát nổ dữ dội 💥!\n\n"
                        f"❌ Toàn bộ nguyên liệu bị thiêu rụi thành tro.\n"
                        f"💔 Sức ép vụ nổ làm chấn động kinh mạch, suy giảm **-{exp_loss} EXP** tu vi!\n"
                        f"📊 EXP Tu vi còn lại: `{updated_player.get('EXP')}` EXP"
                    ),
                    color=discord.Color.dark_red()
                )
            else:
                await self.bot.excel_manager.add_exp(discord_id, 10)
                updated_player = await self.bot.excel_manager.get_player(discord_id)
                embed = discord.Embed(
                    title="💨 LUYỆN ĐAN THẤT BẠI",
                    description=(
                        f"😔 Dược lực không thể ngưng tụ thành đan, nguyên liệu hóa thành khói đen...\n\n"
                        f"❌ Không chế tạo thành công đan dược.\n"
                        f"💡 Lấy kinh nghiệm: Nhận `+10` EXP an ủi. (Tổng EXP: `{updated_player.get('EXP')}`)"
                    ),
                    color=discord.Color.dark_gray()
                )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dung_dan", description="Sử dụng Linh Đan trong túi đồ để tăng Tu vi hoặc Buff Đột Phá")
    @app_commands.describe(ten_dan="Tên loại linh đan muốn sử dụng")
    async def dung_dan(self, interaction: discord.Interaction, ten_dan: str):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        record_activity(discord_id, "dung_dan", self.bot)

        matched_dan = None
        for dan_name in DAN_EFFECTS:
            if ten_dan.strip().lower() in dan_name.lower():
                matched_dan = dan_name
                break

        if not matched_dan:
            await interaction.response.send_message(
                f"❌ Loại đan **{ten_dan}** không tồn tại hoặc không thể dùng. Hãy kiểm tra `/tui_do`!",
                ephemeral=True
            )
            return

        success, msg = await self.bot.excel_manager.use_item(discord_id, matched_dan, 1)
        if not success:
            await interaction.response.send_message(f"❌ {msg}", ephemeral=True)
            return

        effect = DAN_EFFECTS[matched_dan]
        player = await self.bot.excel_manager.get_player(discord_id)

        if effect["type"] == "exp":
            await self.bot.excel_manager.add_exp(discord_id, effect["val"])
            updated_player = await self.bot.excel_manager.get_player(discord_id)
            embed = discord.Embed(
                title="💊 CẮN ĐAN TĂNG TU VI!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào 1 viên **{matched_dan}**, dược lực dâng trào!\n\n"
                    f"✨ Nhận ngay: `+{effect['val']}` EXP Tu Vi!\n"
                    f"📊 Tổng EXP hiện tại: `{updated_player.get('EXP')}` EXP"
                ),
                color=discord.Color.green()
            )
        elif effect["type"] == "exp_buff":
            await self.bot.excel_manager.add_exp(discord_id, effect["val"])
            current_buff = int(player.get("Buff đột phá", 0))
            new_buff = current_buff + effect["buff"]
            await self.bot.excel_manager.update_player(discord_id, {"Buff đột phá": new_buff})
            updated_player = await self.bot.excel_manager.get_player(discord_id)
            embed = discord.Embed(
                title="💊 CẮN THẦN ĐAN THƯỢNG PHẨM!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào **{matched_dan}**, dược lực phát sáng thần thánh!\n\n"
                    f"✨ Nhận ngay: `+{effect['val']}` EXP Tu Vi!\n"
                    f"⚡ Buff Đột Phá: `+{new_buff}%` tỉ lệ thành công!\n"
                    f"📊 Tổng EXP: `{updated_player.get('EXP')}` EXP"
                ),
                color=discord.Color.gold()
            )
        elif effect["type"] == "heal":
            await self.bot.excel_manager.update_player(discord_id, {"HP": 100, "Mana": 100})
            embed = discord.Embed(
                title="💊 CẮN ĐAN PHỤC HỒI!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào **{matched_dan}**!\n\n"
                    f"💚 Sinh lực HP & Mana đã được hồi phục **100%** đầy tràn!"
                ),
                color=discord.Color.blue()
            )
        else: # buff
            current_buff = int(player.get("Buff đột phá", 0))
            new_buff = current_buff + effect["val"]
            await self.bot.excel_manager.update_player(discord_id, {"Buff đột phá": new_buff})
            embed = discord.Embed(
                title="⚡ CẮN ĐAN TRỢ LỰC ĐỘT PHÁ!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào **{matched_dan}**, củng cố căn cơ linh hồn!\n\n"
                    f"✨ Buff Đột Phá tích lũy: `+{new_buff}%` (Sẽ tự kích hoạt khi gõ `/dot_pha`)"
                ),
                color=discord.Color.gold()
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AlchemyCog(bot))
