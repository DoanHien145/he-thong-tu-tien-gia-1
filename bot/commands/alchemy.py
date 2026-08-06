import random
import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger
from bot.config import REALMS
from bot.commands.economy import record_activity

RECIPES = {
    # --- NHẤT PHẨM ---
    "Luyện Khí Đan": {
        "ingredients": {"Tam Diệp Thảo": 2},
        "success_rate": 0.85,
        "explosion_rate": 0.05,
        "exp_loss_on_explosion": 30,
        "type": "exp",
        "effect_val": 40,
        "min_realm_idx": 0,
        "min_realm_name": "Luyện Khí tầng 1",
        "desc": "Linh đan Nhất Phẩm • Yêu cầu Luyện Khí Tầng 1 • Cắn đan +40 EXP"
    },
    "Tụ Khí Đan": {
        "ingredients": {"Tam Diệp Thảo": 2, "U Nhược Hoa": 1},
        "success_rate": 0.70,
        "explosion_rate": 0.08,
        "exp_loss_on_explosion": 50,
        "type": "buff",
        "effect_val": 20,
        "min_realm_idx": 1,
        "min_realm_name": "Luyện Khí tầng 2",
        "desc": "Linh đan Nhất Phẩm • Yêu cầu Luyện Khí Tầng 2 • Buff +20% Đột Phá"
    },
    "Hồi Xuân Đan": {
        "ingredients": {"Tam Diệp Thảo": 3, "U Nhược Hoa": 1},
        "success_rate": 0.80,
        "explosion_rate": 0.05,
        "exp_loss_on_explosion": 20,
        "type": "heal",
        "effect_val": 100,
        "min_realm_idx": 2,
        "min_realm_name": "Luyện Khí tầng 3",
        "desc": "Linh đan Phục Hồi • Yêu cầu Luyện Khí Tầng 3 • Hồi 100 HP & 100 Mana"
    },
    "Thanh Tâm Đan": {
        "ingredients": {"Tam Diệp Thảo": 2, "Bích Ngọc Liên": 1},
        "success_rate": 0.75,
        "explosion_rate": 0.06,
        "exp_loss_on_explosion": 40,
        "type": "exp_buff",
        "effect_val": 100,
        "buff": 10,
        "min_realm_idx": 4,
        "min_realm_name": "Luyện Khí tầng 5",
        "desc": "Linh đan Nhất Phẩm • Yêu cầu Luyện Khí Tầng 5 • Cắn đan +100 EXP & +10% Buff Đột Phá"
    },
    "Ngưng Nguyệt Đan": {
        "ingredients": {"Bích Ngọc Liên": 2, "Cửu Diệp Nguyệt Thảo": 1},
        "success_rate": 0.65,
        "explosion_rate": 0.08,
        "exp_loss_on_explosion": 60,
        "type": "exp",
        "effect_val": 200,
        "min_realm_idx": 6,
        "min_realm_name": "Luyện Khí tầng 7",
        "desc": "Linh đan Nhất Phẩm • Yêu cầu Luyện Khí Tầng 7 • Cắn đan +200 EXP"
    },

    # --- NHỊ PHẨM ---
    "Trúc Cơ Đan": {
        "ingredients": {"U Nhược Hoa": 2, "Xích Viêm Quả": 1},
        "success_rate": 0.55,
        "explosion_rate": 0.10,
        "exp_loss_on_explosion": 100,
        "type": "exp",
        "effect_val": 500,
        "min_realm_idx": 10,
        "min_realm_name": "Trúc Cơ Sơ Kỳ",
        "desc": "Linh đan Nhị Phẩm • Yêu cầu Trúc Cơ Sơ Kỳ • Cắn đan +500 EXP"
    },
    "Tẩy Tủy Đan": {
        "ingredients": {"Xích Viêm Quả": 2, "Lôi Linh Quả": 1},
        "success_rate": 0.40,
        "explosion_rate": 0.12,
        "exp_loss_on_explosion": 200,
        "type": "buff",
        "effect_val": 35,
        "min_realm_idx": 11,
        "min_realm_name": "Trúc Cơ Trung Kỳ",
        "desc": "Linh đan Nhị Phẩm • Yêu cầu Trúc Cơ Trung Kỳ • Buff +35% Đột Phá"
    },
    "Thần Hành Đan": {
        "ingredients": {"Xích Viêm Quả": 1, "Vạn Năm Linh Chi": 1},
        "success_rate": 0.50,
        "explosion_rate": 0.10,
        "exp_loss_on_explosion": 150,
        "type": "buff",
        "effect_val": 25,
        "min_realm_idx": 12,
        "min_realm_name": "Trúc Cơ Hậu Kỳ",
        "desc": "Linh đan Trợ Chiến • Yêu cầu Trúc Cơ Hậu Kỳ • Tăng +25% Né Lôi Kiếp & Đột Phá"
    },
    "Cốt Sủy Đan": {
        "ingredients": {"Hóa Cốt Thảo": 2, "U Nhược Hoa": 2},
        "success_rate": 0.45,
        "explosion_rate": 0.12,
        "exp_loss_on_explosion": 180,
        "type": "exp_buff",
        "effect_val": 1000,
        "buff": 15,
        "min_realm_idx": 13,
        "min_realm_name": "Trúc Cơ Đại Viên Mãn",
        "desc": "Linh đan Nhị Phẩm • Yêu cầu Trúc Cơ Đại Viên Mãn • Cắn đan +1,000 EXP & +15% Buff Đột Phá"
    },
    "Tụ Linh Đan": {
        "ingredients": {"Cửu Diệp Nguyệt Thảo": 2, "Xích Viêm Quả": 1},
        "success_rate": 0.42,
        "explosion_rate": 0.14,
        "exp_loss_on_explosion": 220,
        "type": "exp",
        "effect_val": 2000,
        "min_realm_idx": 14,
        "min_realm_name": "Kim Đan Sơ Kỳ",
        "desc": "Linh đan Nhị Phẩm • Yêu cầu Kim Đan Sơ Kỳ • Cắn đan +2,000 EXP"
    },

    # --- TAM PHẨM ---
    "Kim Đan Bảo Đan": {
        "ingredients": {"Lôi Linh Quả": 2, "Vạn Năm Linh Chi": 1},
        "success_rate": 0.30,
        "explosion_rate": 0.15,
        "exp_loss_on_explosion": 500,
        "type": "exp_buff",
        "effect_val": 3500,
        "buff": 30,
        "min_realm_idx": 15,
        "min_realm_name": "Kim Đan Trung Kỳ",
        "desc": "Linh đan Tam Phẩm • Yêu cầu Kim Đan Trung Kỳ • Cắn đan +3,500 EXP & +30% Buff Đột Phá"
    },
    "Ngũ Hành Linh Đan": {
        "ingredients": {"Ngũ Hành Quả": 2, "Lôi Linh Quả": 1},
        "success_rate": 0.28,
        "explosion_rate": 0.16,
        "exp_loss_on_explosion": 600,
        "type": "exp_buff",
        "effect_val": 5000,
        "buff": 20,
        "min_realm_idx": 16,
        "min_realm_name": "Kim Đan Hậu Kỳ",
        "desc": "Linh đan Tam Phẩm • Yêu cầu Kim Đan Hậu Kỳ • Cắn đan +5,000 EXP & +20% Buff Đột Phá"
    },
    "Địa Mẫu Đan": {
        "ingredients": {"Địa Mẫu Tinh Tủy": 2, "Vạn Năm Linh Chi": 1},
        "success_rate": 0.25,
        "explosion_rate": 0.18,
        "exp_loss_on_explosion": 800,
        "type": "exp",
        "effect_val": 8000,
        "min_realm_idx": 17,
        "min_realm_name": "Kim Đan Đại Viên Mãn",
        "desc": "Linh đan Tam Phẩm • Yêu cầu Kim Đan Đại Viên Mãn • Cắn đan +8,000 EXP"
    },

    # --- TỨ PHẨM ---
    "Nguyên Anh Đan": {
        "ingredients": {"Vạn Năm Linh Chi": 2, "Thiên Niên Tuyết Liên": 1},
        "success_rate": 0.20,
        "explosion_rate": 0.20,
        "exp_loss_on_explosion": 1000,
        "type": "exp",
        "effect_val": 15000,
        "min_realm_idx": 18,
        "min_realm_name": "Nguyên Anh Sơ Kỳ",
        "desc": "Linh đan Tứ Phẩm • Yêu cầu Nguyên Anh Sơ Kỳ • Cắn đan +15,000 EXP"
    },
    "Chân Long Đan": {
        "ingredients": {"Long Dược Căn": 2, "Thiên Niên Tuyết Liên": 1},
        "success_rate": 0.18,
        "explosion_rate": 0.22,
        "exp_loss_on_explosion": 1500,
        "type": "exp_buff",
        "effect_val": 25000,
        "buff": 35,
        "min_realm_idx": 19,
        "min_realm_name": "Nguyên Anh Trung Kỳ",
        "desc": "Linh đan Tứ Phẩm • Yêu cầu Nguyên Anh Trung Kỳ • Cắn đan +25,000 EXP & +35% Buff Đột Phá"
    },
    "Phượng Hoàng Niết Bàn Đan": {
        "ingredients": {"Phượng Hoàng Hoa": 2, "Long Dược Căn": 1},
        "success_rate": 0.15,
        "explosion_rate": 0.25,
        "exp_loss_on_explosion": 2000,
        "type": "exp_heal",
        "effect_val": 40000,
        "min_realm_idx": 20,
        "min_realm_name": "Nguyên Anh Hậu Kỳ",
        "desc": "Thần đan Tứ Phẩm • Yêu cầu Nguyên Anh Hậu Kỳ • Cắn đan +40,000 EXP & Hồi HP/Mana"
    },

    # --- NGŨ PHẨM ---
    "Hóa Thần Đan": {
        "ingredients": {"Hóa Thần Thảo": 2, "Thái Sơ Linh Chi": 1},
        "success_rate": 0.12,
        "explosion_rate": 0.28,
        "exp_loss_on_explosion": 3000,
        "type": "exp_buff",
        "effect_val": 80000,
        "buff": 50,
        "min_realm_idx": 22,
        "min_realm_name": "Hóa Thần Sơ Kỳ",
        "desc": "Thượng Cổ Thần Đan • Yêu cầu Hóa Thần Sơ Kỳ • Cắn đan +80,000 EXP & +50% Buff Đột Phá"
    },
    "Thái Sơ Hóa Đan": {
        "ingredients": {"Thái Sơ Linh Chi": 2, "Hóa Thần Thảo": 2},
        "success_rate": 0.08,
        "explosion_rate": 0.35,
        "exp_loss_on_explosion": 5000,
        "type": "exp_buff",
        "effect_val": 150000,
        "buff": 60,
        "min_realm_idx": 23,
        "min_realm_name": "Hóa Thần Trung Kỳ",
        "desc": "Chí Tôn Chí Bảo • Yêu cầu Hóa Thần Trung Kỳ • Cắn đan +150,000 EXP & +60% Buff Đột Phá"
    }
}

DAN_EFFECTS = {
    "Luyện Khí Đan": {"type": "exp", "val": 40, "min_realm_idx": 0, "min_realm_name": "Luyện Khí tầng 1", "backfire_exp": 50, "desc": "Tăng +40 EXP tu vi!"},
    "Tụ Khí Đan": {"type": "buff", "val": 20, "min_realm_idx": 1, "min_realm_name": "Luyện Khí tầng 2", "backfire_exp": 80, "desc": "Gia tăng +20% tỷ lệ thành công cho lần Đột Phá tiếp theo!"},
    "Hồi Xuân Đan": {"type": "heal", "val": 100, "min_realm_idx": 2, "min_realm_name": "Luyện Khí tầng 3", "backfire_exp": 100, "desc": "Phục hồi 100 HP & 100 Mana lập tức!"},
    "Thanh Tâm Đan": {"type": "exp_buff", "val": 100, "buff": 10, "min_realm_idx": 4, "min_realm_name": "Luyện Khí tầng 5", "backfire_exp": 150, "desc": "Tăng +100 EXP & +10% Buff Đột Phá!"},
    "Ngưng Nguyệt Đan": {"type": "exp", "val": 200, "min_realm_idx": 6, "min_realm_name": "Luyện Khí tầng 7", "backfire_exp": 250, "desc": "Tăng +200 EXP tu vi!"},

    "Trúc Cơ Đan": {"type": "exp", "val": 500, "min_realm_idx": 10, "min_realm_name": "Trúc Cơ Sơ Kỳ", "backfire_exp": 400, "desc": "Tăng +500 EXP tu vi!"},
    "Tẩy Tủy Đan": {"type": "buff", "val": 35, "min_realm_idx": 11, "min_realm_name": "Trúc Cơ Trung Kỳ", "backfire_exp": 500, "desc": "Gia tăng +35% tỷ lệ thành công cho lần Đột Phá tiếp theo!"},
    "Thần Hành Đan": {"type": "buff", "val": 25, "min_realm_idx": 12, "min_realm_name": "Trúc Cơ Hậu Kỳ", "backfire_exp": 600, "desc": "Gia tăng +25% Tỉ lệ Đột Phá chấn áp Tâm Ma!"},
    "Cốt Sủy Đan": {"type": "exp_buff", "val": 1000, "buff": 15, "min_realm_idx": 13, "min_realm_name": "Trúc Cơ Đại Viên Mãn", "backfire_exp": 800, "desc": "Tăng +1000 EXP & +15% Buff Đột Phá!"},
    "Tụ Linh Đan": {"type": "exp", "val": 2000, "min_realm_idx": 14, "min_realm_name": "Kim Đan Sơ Kỳ", "backfire_exp": 1200, "desc": "Tăng +2000 EXP tu vi!"},

    "Kim Đan Bảo Đan": {"type": "exp_buff", "val": 3500, "buff": 30, "min_realm_idx": 15, "min_realm_name": "Kim Đan Trung Kỳ", "backfire_exp": 2500, "desc": "Tăng +3500 EXP & +30% Buff Đột Phá!"},
    "Ngũ Hành Linh Đan": {"type": "exp_buff", "val": 5000, "buff": 20, "min_realm_idx": 16, "min_realm_name": "Kim Đan Hậu Kỳ", "backfire_exp": 3500, "desc": "Tăng +5000 EXP & +20% Buff Đột Phá!"},
    "Địa Mẫu Đan": {"type": "exp", "val": 8000, "min_realm_idx": 17, "min_realm_name": "Kim Đan Đại Viên Mãn", "backfire_exp": 5000, "desc": "Tăng +8000 EXP tu vi!"},

    "Nguyên Anh Đan": {"type": "exp", "val": 15000, "min_realm_idx": 18, "min_realm_name": "Nguyên Anh Sơ Kỳ", "backfire_exp": 10000, "desc": "Tăng +15,000 EXP tu vi!"},
    "Chân Long Đan": {"type": "exp_buff", "val": 25000, "buff": 35, "min_realm_idx": 19, "min_realm_name": "Nguyên Anh Trung Kỳ", "backfire_exp": 15000, "desc": "Tăng +25,000 EXP & +35% Buff Đột Phá!"},
    "Phượng Hoàng Niết Bàn Đan": {"type": "exp_heal", "val": 40000, "min_realm_idx": 20, "min_realm_name": "Nguyên Anh Hậu Kỳ", "backfire_exp": 20000, "desc": "Tăng +40,000 EXP & Hồi HP/Mana đầy tràn!"},

    "Hóa Thần Đan": {"type": "exp_buff", "val": 80000, "buff": 50, "min_realm_idx": 22, "min_realm_name": "Hóa Thần Sơ Kỳ", "backfire_exp": 40000, "desc": "Tăng +80,000 EXP & +50% Buff Đột Phá!"},
    "Thái Sơ Hóa Đan": {"type": "exp_buff", "val": 150000, "buff": 60, "min_realm_idx": 23, "min_realm_name": "Hóa Thần Trung Kỳ", "backfire_exp": 80000, "desc": "Tăng +150,000 EXP & +60% Buff Đột Phá!"}
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
                req_realm = recipe.get("min_realm_name", "Luyện Khí tầng 1")
                embed.add_field(
                    name=f"🧪 {dan_name} (Tỉ lệ thành công: {int(recipe['success_rate']*100)}%)",
                    value=f"└ 🌿 Nguyên liệu: {ing_str}\n└ ☯ Cảnh giới dùng: **{req_realm}**\n└ ✨ Tác dụng: {recipe['desc']}",
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
            await self.bot.excel_manager.save()
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
                await self.bot.excel_manager.save()
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
                await self.bot.excel_manager.save()
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

    @che_dan.autocomplete("ten_dan")
    async def che_dan_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        items = list(RECIPES.keys())
        matches = [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()
        ]
        return matches[:25]

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

        # Check if player has the pill in inventory
        inventory = await self.bot.excel_manager.get_inventory(discord_id)
        if inventory.get(matched_dan, 0) <= 0:
            await interaction.response.send_message(
                f"❌ Bạn không có linh đan **{matched_dan}** trong Túi Đồ! Hãy dùng `/che_dan` hoặc `/shop` để sở hữu.",
                ephemeral=True
            )
            return

        effect = DAN_EFFECTS[matched_dan]
        player = await self.bot.excel_manager.get_player(discord_id)
        current_realm = player.get("Cảnh giới", "Luyện Khí tầng 1")

        # Determine realm index
        player_realm_idx = next((i for i, r in enumerate(REALMS) if r["name"] == current_realm), 0)
        min_realm_idx = effect.get("min_realm_idx", 0)
        min_realm_name = effect.get("min_realm_name", "Luyện Khí tầng 1")

        # Level check: If user realm is too low, trigger BACKFIRE!
        if player_realm_idx < min_realm_idx:
            # Deduct the pill (it was consumed)
            await self.bot.excel_manager.use_item(discord_id, matched_dan, 1)

            backfire_exp = effect.get("backfire_exp", 500)
            current_exp = int(player.get("EXP", 0))
            new_exp = max(0, current_exp - backfire_exp)
            await self.bot.excel_manager.update_player(discord_id, {"EXP": new_exp})
            await self.bot.excel_manager.save()
            updated_player = await self.bot.excel_manager.get_player(discord_id)

            embed = discord.Embed(
                title="💥 DƯỢC LỰC BỘC PHÁT — BỊ PHẢN PHỆ TỔN THƯƠNG KINHMẠCH!",
                description=(
                    f"😱 Cảnh giới của **{player.get('Tên')}** hiện tại mới là **{current_realm}**, "
                    f"không thể gánh vác dược lực cuồng bạo của **{matched_dan}** (Cảnh giới yêu cầu: **{min_realm_name}**)!\n\n"
                    f"☠️ Cố chấp nuốt thần đan vượt cấp khiến cuồng phong linh khí xé rách kinh mạch!\n"
                    f"💔 Bị phản phệ sụt giảm ngay **-{backfire_exp} EXP** tu vi!\n"
                    f"📊 EXP Tu Vi còn lại: `{updated_player.get('EXP')}` EXP"
                ),
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Normal usage when realm condition is met
        success, msg = await self.bot.excel_manager.use_item(discord_id, matched_dan, 1)
        if not success:
            await interaction.response.send_message(f"❌ {msg}", ephemeral=True)
            return

        if effect["type"] == "exp":
            await self.bot.excel_manager.add_exp(discord_id, effect["val"])
            await self.bot.excel_manager.save()
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
            await self.bot.excel_manager.save()
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
        elif effect["type"] == "exp_heal":
            await self.bot.excel_manager.add_exp(discord_id, effect["val"])
            await self.bot.excel_manager.update_player(discord_id, {"HP": 100, "Mana": 100})
            await self.bot.excel_manager.save()
            updated_player = await self.bot.excel_manager.get_player(discord_id)
            embed = discord.Embed(
                title="🔥 CẮN THẦN ĐAN NIẾT BÀN!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào **{matched_dan}**, phượng hoàng thần hỏa tẩy lễ toàn thân!\n\n"
                    f"✨ Nhận ngay: `+{effect['val']}` EXP Tu Vi!\n"
                    f"💚 Sinh lực HP & Mana hồi phục **100%** tràn đầy!\n"
                    f"📊 Tổng EXP: `{updated_player.get('EXP')}` EXP"
                ),
                color=discord.Color.purple()
            )
        elif effect["type"] == "heal":
            await self.bot.excel_manager.update_player(discord_id, {"HP": 100, "Mana": 100})
            await self.bot.excel_manager.save()
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
            await self.bot.excel_manager.save()
            embed = discord.Embed(
                title="⚡ CẮN ĐAN TRỢ LỰC ĐỘT PHÁ!",
                description=(
                    f"**{player.get('Tên')}** nuốt vào **{matched_dan}**, củng cố căn cơ linh hồn!\n\n"
                    f"✨ Buff Đột Phá tích lũy: `+{new_buff}%` (Sẽ tự kích hoạt khi gõ `/dot_pha`)"
                ),
                color=discord.Color.gold()
            )

        await interaction.response.send_message(embed=embed)

    @dung_dan.autocomplete("ten_dan")
    async def dung_dan_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        items = list(DAN_EFFECTS.keys())
        matches = [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()
        ]
        return matches[:25]

async def setup(bot):
    await bot.add_cog(AlchemyCog(bot))
