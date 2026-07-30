import random
import time
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

SHOP_ITEMS = {
    "Luyện Khí Đan": {"price": 150, "type": "dan", "desc": "Linh đan Nhất Phẩm • Cắn đan nhận ngay +300 EXP tu vi"},
    "Tụ Khí Đan": {"price": 300, "type": "dan", "desc": "Linh đan Nhất Phẩm • Gia tăng +20% tỷ lệ đột phá thành công"},
    "Trúc Cơ Đan": {"price": 800, "type": "dan", "desc": "Linh đan Nhị Phẩm • Cắn đan nhận ngay +1500 EXP tu vi"},
    "Tẩy Tủy Đan": {"price": 1500, "type": "dan", "desc": "Linh đan Nhị Phẩm • Gia tăng +35% tỷ lệ đột phá thành công"},
    "Tam Diệp Thảo": {"price": 50, "type": "nguyen_lieu", "desc": "Linh thảo cơ bản dùng để luyện chế Luyện Khí Đan & Tụ Khí Đan"},
    "U Nhược Hoa": {"price": 120, "type": "nguyen_lieu", "desc": "Dược liệu trung cấp dùng để luyện chế Trúc Cơ Đan"},
    "Xích Viêm Quả": {"price": 300, "type": "nguyen_lieu", "desc": "Linh quả hiếm dùng để luyện chế Tẩy Tủy Đan & Kim Đan"},
    "Lôi Linh Quả": {"price": 600, "type": "nguyen_lieu", "desc": "Linh quả cực hiếm hấp thụ lôi đình dùng luyện Kim Đan"}
}

USER_ACTIVITIES: dict[str, set[str]] = {}
USER_QUEST_CLAIMS: dict[str, set[str]] = {}

def record_activity(discord_id: str, activity_name: str):
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if key not in USER_ACTIVITIES:
        USER_ACTIVITIES[key] = set()
    USER_ACTIVITIES[key].add(activity_name)

def has_activity(discord_id: str, activity_name: str) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    return activity_name in USER_ACTIVITIES.get(key, set())

def is_quest_claimed(discord_id: str, quest_id: str) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    return quest_id in USER_QUEST_CLAIMS.get(key, set())

def mark_quest_claimed(discord_id: str, quest_id: str):
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if key not in USER_QUEST_CLAIMS:
        USER_QUEST_CLAIMS[key] = set()
    USER_QUEST_CLAIMS[key].add(quest_id)

QUESTS = [
    {
        "id": "1",
        "name": "📜 Siêng Năng Báo Danh",
        "activity_code": "diem_danh",
        "req_command": "/diem_danh",
        "desc": "Báo danh tông môn hàng ngày để thể hiện tinh thần mẫn cán.",
        "reward_lt": 150,
        "reward_exp": 100,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Chạy lệnh `/diem_danh` ít nhất 1 lần trong ngày!"
    },
    {
        "id": "2",
        "name": "🧘 Khổ Luyện Thành Tài",
        "activity_code": "tu_luyen",
        "req_command": "/tu_luyen",
        "desc": "Tiến hành bế quan tu luyện hấp thụ linh khí thiên địa.",
        "reward_lt": 200,
        "reward_exp": 150,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Chạy lệnh `/tu_luyen` ít nhất 1 lần trong ngày!"
    },
    {
        "id": "3",
        "name": "🧪 Sơ Nhập Đan Đạo",
        "activity_code": "che_dan",
        "req_command": "/che_dan",
        "desc": "Khai mở Dược Lô luyện đan hoặc sở hữu linh đan trong túi đồ.",
        "reward_lt": 250,
        "reward_exp": 200,
        "reward_item": "U Nhược Hoa",
        "hint": "Thực hiện `/che_dan` HOẶC sở hữu đan dược trong `/tui_do`!"
    },
    {
        "id": "4",
        "name": "💊 Phục Dụng Linh Đan",
        "activity_code": "dung_dan",
        "req_command": "/dung_dan",
        "desc": "Sử dụng 1 viên Linh Đan bất kỳ để tăng cường công lực tu vi.",
        "reward_lt": 300,
        "reward_exp": 250,
        "reward_item": "U Nhược Hoa",
        "hint": "Chạy lệnh `/dung_dan [tên_đan]` ít nhất 1 lần hôm nay!"
    },
    {
        "id": "5",
        "name": "🛍️ Giao Thương Bảo Các",
        "activity_code": "mua_shop",
        "req_command": "/mua",
        "desc": "Ghé thăm Bảo Các Tông Môn mua sắm đan dược hoặc dược liệu.",
        "reward_lt": 250,
        "reward_exp": 150,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Ghé `/shop` và mua bằng lệnh `/mua [tên_vật_phẩm]`!"
    },
    {
        "id": "6",
        "name": "⛩️ Thám Hiểm Bí Cảnh",
        "activity_code": "sukien",
        "req_command": "/sukien",
        "desc": "Tham gia sự kiện ngẫu nhiên khám phá bí cảnh Tông môn.",
        "reward_lt": 350,
        "reward_exp": 300,
        "reward_item": "Xích Viêm Quả",
        "hint": "Chạy lệnh `/sukien` để mạo hiểm tìm kỳ duyên hôm nay!"
    },
    {
        "id": "7",
        "name": "⚔️ Trảm Yêu Tiêu Ma (Quyết Chiến)",
        "activity_code": "tram_yeu",
        "req_command": "HP ≥ 20 & MP ≥ 20",
        "desc": "Tiêu hao 20 HP & 20 Mana để trừ yêu diệt ma hộ vệ sơn môn.",
        "reward_lt": 600,
        "reward_exp": 500,
        "reward_item": "Lôi Linh Quả",
        "hint": "Yêu cầu có HP ≥ 20 và Mana ≥ 20 trong người để nghênh chiến!"
    }
]

def check_quest_condition(discord_id: str, quest: dict, player: dict, inventory: dict) -> tuple[bool, str]:
    code = quest["activity_code"]
    today = datetime.now().strftime("%Y-%m-%d")

    if code == "diem_danh":
        if player.get("Ngày điểm danh") == today or has_activity(discord_id, "diem_danh"):
            return True, "Đã báo danh thành công!"
        return False, "Bạn chưa báo danh hôm nay. Hãy chạy lệnh `/diem_danh` trước!"

    if code == "tu_luyen":
        if has_activity(discord_id, "tu_luyen") or int(player.get("EXP", 0)) >= 50:
            return True, "Đã hoàn thành tu luyện!"
        return False, "Bạn chưa bế quan tu luyện hôm nay. Hãy chạy lệnh `/tu_luyen` trước!"

    if code == "che_dan":
        has_dan_in_inv = any("Đan" in item for item, cnt in inventory.items() if cnt > 0)
        if has_activity(discord_id, "che_dan") or has_dan_in_inv:
            return True, "Đã có đan dược / hoàn thành chế đan!"
        return False, "Bạn chưa chế đan hoặc không có đan dược trong túi. Hãy dùng lệnh `/che_dan` hoặc sở hữu đan dược!"

    if code == "dung_dan":
        if has_activity(discord_id, "dung_dan"):
            return True, "Đã cắn đan dược hôm nay!"
        return False, "Bạn chưa sử dụng linh đan hôm nay. Hãy dùng lệnh `/dung_dan [tên_đan]` trước!"

    if code == "mua_shop":
        if has_activity(discord_id, "mua_shop"):
            return True, "Đã giao dịch mua hàng tại Bảo Các!"
        return False, "Bạn chưa mua hàng tại Bảo Các. Hãy xem `/shop` và mua bằng `/mua [tên_vật_phẩm]`!"

    if code == "sukien":
        if has_activity(discord_id, "sukien"):
            return True, "Đã tham gia sự kiện bí cảnh!"
        return False, "Bạn chưa tham gia sự kiện hôm nay. Hãy chạy lệnh `/sukien` trước!"

    if code == "tram_yeu":
        hp = int(player.get("HP", 100))
        mana = int(player.get("Mana", 100))
        if hp >= 20 and mana >= 20:
            return True, "Đủ sinh lực chiến đấu!"
        return False, f"Bạn không đủ sinh lực để trảm yêu (Cần HP ≥ 20 & MP ≥ 20. Hiện tại: HP {hp}, MP {mana})!"

    return False, "Chưa hoàn thành điều kiện."

RANDOM_EVENTS = [
    {
        "title": "🌟 Linh Khí Bộc Phát",
        "desc": "Trời đất rung chuyển, linh khí nồng đậm bộc phát tại Tông Môn! Bạn lập tức ngồi xếp bằng hấp thụ.",
        "exp": 150,
        "lt": 200,
        "item": "Tam Diệp Thảo",
        "weight": 50
    },
    {
        "title": "⛩️ Bí Cảnh Thượng Cổ Khai Mở",
        "desc": "Một khe nứt bí cảnh thượng cổ xuất hiện! Bạn tiến vào khám phá và tìm thấy dược liệu trung cấp.",
        "exp": 300,
        "lt": 350,
        "item": "U Nhược Hoa",
        "weight": 30
    },
    {
        "title": "🔥 Phát Hiện Linh Quả Hiếm",
        "desc": "Dưới chân vách đá sương mù, bạn tìm thấy Linh Quả hấp thu linh khí thiên địa!",
        "exp": 450,
        "lt": 500,
        "item": "Xích Viêm Quả",
        "weight": 14
    },
    {
        "title": "👴 Lão Tổ Truyền Di Bảo (Cực Hiếm)",
        "desc": "Thái Thượng Đại Lão đăng đài ban thưởng Lôi Linh Quả cực kỳ quý hiếm!",
        "exp": 800,
        "lt": 800,
        "item": "Lôi Linh Quả",
        "weight": 6
    },
    {
        "title": "🎁 Túi Trữ Đồ Vô Chủ",
        "desc": "Bên bờ suối, bạn nhặt được một chiếc túi trữ đồ của cao nhân xưa để lại!",
        "exp": 250,
        "lt": 600,
        "item": "Xích Viêm Quả",
        "weight": 10
    }
]

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_cooldowns: dict[str, float] = {}  # discord_id -> timestamp
        self.shop_last_refresh: float = 0
        self.shop_stock: dict[str, dict] = {}  # item_name -> {"price": int, "stock": int, "max_stock": int, "type": str, "desc": str}

    def refresh_shop_if_needed(self):
        now = time.time()
        # Reset every 5 minutes (300 seconds)
        if now - self.shop_last_refresh >= 300 or not self.shop_stock:
            self.shop_last_refresh = now
            self.shop_stock = {}
            all_items = list(SHOP_ITEMS.items())
            # Randomly select 4 to 7 items to sell
            num_items = random.randint(4, min(7, len(all_items)))
            chosen_items = random.sample(all_items, num_items)

            for name, info in chosen_items:
                stock_qty = random.randint(1, 8)
                self.shop_stock[name] = {
                    "price": info["price"],
                    "stock": stock_qty,
                    "max_stock": stock_qty,
                    "type": info["type"],
                    "desc": info["desc"]
                }

    def get_time_until_reset(self) -> str:
        now = time.time()
        remaining = max(0, int(300 - (now - self.shop_last_refresh)))
        m, s = divmod(remaining, 60)
        return f"{m}m {s}s"

    @app_commands.command(name="shop", description="Xem Bảo Các Tông Môn — Cửa hàng Linh Đan & Nguyên Liệu (Reset 5p/lần)")
    async def shop(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        self.refresh_shop_if_needed()
        reset_time = self.get_time_until_reset()

        embed = discord.Embed(
            title="🏪 Bảo Các Tông Môn — Hàng Giới Hạn (Reset 5p/lần)",
            description=(
                "Bảo Các vừa nhập đợt vật phẩm mới với số lượng có hạn!\n"
                "Sử dụng Linh Thạch 💎 để mua Linh Đan & Nguyên Liệu.\n"
                "Dùng lệnh: `/mua [tên_vật_phẩm] [số_lượng]`\n"
                f"⏱️ **Làm mới kho hàng sau**: `{reset_time}`"
            ),
            color=discord.Color.gold()
        )

        for name, info in self.shop_stock.items():
            type_badge = "🧪 Linh Đan" if info["type"] == "dan" else "🌿 Dược Liệu"
            stock_str = f"📦 Còn lại: `{info['stock']}/{info['max_stock']}` cái" if info['stock'] > 0 else "❌ **ĐÃ HẾT HÀNG**"
            embed.add_field(
                name=f"{type_badge} {name} — Giá: `{info['price']}` 💎",
                value=f"└ *{info['desc']}*\n└ {stock_str}",
                inline=False
            )

        embed.set_footer(text=f"Bảo Các Tông Môn • Tự động đổi hàng & số lượng ngẫu nhiên sau 5 phút (Còn: {reset_time})")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mua", description="Mua Linh Đan hoặc Nguyên Liệu từ Bảo Các Tông Môn")
    @app_commands.describe(vat_pham="Tên vật phẩm (ví dụ: Luyện Khí Đan, Tam Diệp Thảo)", so_luong="Số lượng muốn mua")
    async def mua(self, interaction: discord.Interaction, vat_pham: str, so_luong: int = 1):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        if so_luong <= 0:
            await interaction.response.send_message("❌ Số lượng mua phải lớn hơn 0!", ephemeral=True)
            return

        self.refresh_shop_if_needed()
        reset_time = self.get_time_until_reset()

        matched_item = None
        for item_name in self.shop_stock:
            if vat_pham.strip().lower() in item_name.lower():
                matched_item = item_name
                break

        if not matched_item:
            await interaction.response.send_message(
                f"❌ Bảo Các hiện không bán hoặc chưa có vật phẩm **{vat_pham}** trong đợt này!\n"
                f"Dùng `/shop` để xem các món đang sẵn hàng. Đợt hàng mới sẽ về sau `{reset_time}`.",
                ephemeral=True
            )
            return

        item_info = self.shop_stock[matched_item]
        available_stock = item_info["stock"]

        if available_stock <= 0:
            await interaction.response.send_message(
                f"❌ Vật phẩm **{matched_item}** đã hết hàng hoàn toàn trong Bảo Các đợt này!\n"
                f"Vui lòng đợi đợt nhập hàng tiếp theo sau `{reset_time}`.",
                ephemeral=True
            )
            return

        if so_luong > available_stock:
            await interaction.response.send_message(
                f"❌ Bảo Các hiện chỉ còn **{available_stock}x {matched_item}** (không đủ {so_luong})!\n"
                f"Vui lòng điều chỉnh lại số lượng mua.",
                ephemeral=True
            )
            return

        total_cost = item_info["price"] * so_luong

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_lt = int(player.get("Linh thạch", 0))

        if current_lt < total_cost:
            embed = discord.Embed(
                title="💸 Linh Thạch Không Đủ",
                description=(
                    f"**{player.get('Tên')}** muốn mua **{so_luong}x {matched_item}**!\n"
                    f"💰 Tổng chi phí: `{total_cost}` Linh Thạch\n"
                    f"💎 Linh Thạch hiện có: `{current_lt}` Linh Thạch\n"
                    f"❌ Còn thiếu: `{total_cost - current_lt}` Linh Thạch nữa. Hãy làm `/nhiemvu` hoặc `/diem_danh`!"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Record activity for shopping quest
        record_activity(discord_id, "mua_shop")

        # Deduct stock
        self.shop_stock[matched_item]["stock"] -= so_luong

        # Deduct cost & Add item to inventory
        await self.bot.excel_manager.add_linh_thach(discord_id, -total_cost)
        await self.bot.excel_manager.add_item(discord_id, matched_item, so_luong)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title="🛒 Mua Sắm Thành Công!",
            description=(
                f"🎉 **{player.get('Tên')}** đã mua thành công **{so_luong}x {matched_item}** từ Bảo Các!\n"
                f"💸 Đã thanh toán: `{total_cost}` 💎 Linh Thạch\n"
                f"💎 Linh Thạch còn lại: `{updated_player.get('Linh thạch')}` 💎\n"
                f"📦 Tồn kho còn lại trong Bảo Các: `{self.shop_stock[matched_item]['stock']}` cái\n\n"
                f"🎒 Vật phẩm đã nằm trong túi đồ! Dùng `/tui_do` để kiểm tra hoặc `/dung_dan` để sử dụng."
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nhiemvu", description="Bảng Nhiệm Vụ Hoạt Động Tông Môn — Hoàn thành hoạt động để nhận thưởng!")
    @app_commands.describe(chon_nhiem_vu="Nhập số (1-7) để nhận thưởng nhiệm vụ tương ứng (để trống để xem tiến độ)")
    async def nhiemvu(self, interaction: discord.Interaction, chon_nhiem_vu: str = ""):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name
        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        inventory = await self.bot.excel_manager.get_inventory(discord_id)

        if not chon_nhiem_vu:
            # Show list of quests with live activity status
            embed = discord.Embed(
                title="📜 BẢNG NHIỆM VỤ HOẠT ĐỘNG TÔNG MÔN",
                description=(
                    f"Chào tu sĩ **{player.get('Tên')}**! Hãy hoàn thành các hoạt động hằng ngày bên dưới để nhận thưởng.\n"
                    f"👉 **Cú pháp nhận thưởng**: `/nhiemvu [số 1-7]`"
                ),
                color=discord.Color.blue()
            )

            for idx, q in enumerate(QUESTS, 1):
                claimed = is_quest_claimed(discord_id, q["id"])
                ok, note = check_quest_condition(discord_id, q, player, inventory)

                if claimed:
                    status = "🟢 `[ĐÃ HOÀN THÀNH HÔM NAY]`"
                elif ok:
                    status = f"✨ `[ĐÃ ĐỦ ĐIỀU KIỆN — Gõ /nhiemvu {idx} để nhận]`"
                else:
                    status = f"🔒 `[CHƯA HOÀN THÀNH — {q['req_command']}]`"

                embed.add_field(
                    name=f"Nhiệm vụ #{idx}: {q['name']} — {status}",
                    value=(
                        f"└ *{q['desc']}*\n"
                        f"└ 🎯 **Yêu cầu**: `{q['req_command']}`\n"
                        f"└ 🎁 **Thưởng**: `+{q['reward_lt']}` 💎 LT | `+{q['reward_exp']}` ✨ EXP | `1x {q['reward_item']}` 🌿"
                    ),
                    inline=False
                )

            embed.set_footer(text="Nhiệm vụ tông môn làm mới mỗi ngày • Hãy siêng năng hoàn thành!")
            await interaction.response.send_message(embed=embed)
            return

        # Execute / claim selected quest
        selected_quest = None
        cleaned_input = chon_nhiem_vu.strip()

        if cleaned_input in [str(i) for i in range(1, len(QUESTS) + 1)]:
            idx = int(cleaned_input) - 1
            selected_quest = QUESTS[idx]
        else:
            for q in QUESTS:
                if cleaned_input.lower() in q["name"].lower():
                    selected_quest = q
                    break

        if not selected_quest:
            await interaction.response.send_message(
                f"❌ Số nhiệm vụ không hợp lệ (1-{len(QUESTS)}). Gõ `/nhiemvu` để xem Bảng Nhiệm Vụ!",
                ephemeral=True
            )
            return

        # Check if already claimed today
        if is_quest_claimed(discord_id, selected_quest["id"]):
            embed = discord.Embed(
                title="✅ Đã Nhận Thưởng Hôm Nay",
                description=(
                    f"Tu sĩ **{player.get('Tên')}** đã hoàn thành và nhận thưởng nhiệm vụ **{selected_quest['name']}** hôm nay rồi!\n\n"
                    f"🌅 Hãy quay lại làm nhiệm vụ này vào ngày mai."
                ),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check activity requirement
        ok, reason = check_quest_condition(discord_id, selected_quest, player, inventory)
        if not ok:
            embed = discord.Embed(
                title="🔒 Chưa Hoàn Thành Hoạt Động Yêu Cầu",
                description=(
                    f"Tu sĩ **{player.get('Tên')}** chưa đủ điều kiện nhận thưởng **{selected_quest['name']}**!\n\n"
                    f"❌ **Lý do**: {reason}\n"
                    f"💡 **Hướng dẫn**: {selected_quest['hint']}"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Deduct stats if special combat quest
        if selected_quest["activity_code"] == "tram_yeu":
            hp = int(player.get("HP", 100))
            mana = int(player.get("Mana", 100))
            await self.bot.excel_manager.update_player(discord_id, {
                "HP": max(10, hp - 20),
                "Mana": max(10, mana - 20)
            })

        # Grant rewards & Mark claimed
        mark_quest_claimed(discord_id, selected_quest["id"])
        await self.bot.excel_manager.add_exp(discord_id, selected_quest["reward_exp"])
        await self.bot.excel_manager.add_linh_thach(discord_id, selected_quest["reward_lt"])
        await self.bot.excel_manager.add_item(discord_id, selected_quest["reward_item"], 1)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title="🎉 HOÀN THÀNH NHIỆM VỤ TÔNG MÔN!",
            description=(
                f"Tu sĩ **{player.get('Tên')}** đã hoàn tất hoạt động và nhận thưởng **{selected_quest['name']}**!\n\n"
                f"🎁 **Phần thưởng nhận được**:\n"
                f"• `+{selected_quest['reward_lt']}` 💎 Linh Thạch\n"
                f"• `+{selected_quest['reward_exp']}` ✨ EXP Tu vi\n"
                f"• `1x {selected_quest['reward_item']}` 🌿 (Đã chuyển vào Túi Đồ)\n\n"
                f"📊 Linh Thạch hiện tại: `{updated_player.get('Linh thạch')}` 💎 | EXP: `{updated_player.get('EXP')}` ✨"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sukien", description="Tham gia Sự Kiện Ngẫu Nhiên Tông Môn để thử vận may nhận cơ duyên! (Hồi chiêu 5 phút)")
    async def sukien(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name
        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)

        # Record activity for sukien quest
        record_activity(discord_id, "sukien")

        # Check 5-minute cooldown (300 seconds)
        now = time.time()
        last_used = self.event_cooldowns.get(discord_id, 0)
        cooldown_duration = 300  # 5 minutes

        if now - last_used < cooldown_duration:
            remaining = int(cooldown_duration - (now - last_used))
            minutes = remaining // 60
            seconds = remaining % 60
            time_str = f"{minutes} phút {seconds} giây" if minutes > 0 else f"{seconds} giây"

            embed = discord.Embed(
                title="⏳ Đang Trong Thời Gian Chờ (Cooldown)",
                description=(
                    f"Tu sĩ **{player.get('Tên')}** vừa mới tham gia sự kiện gần đây!\n\n"
                    f"🛑 Hãy tĩnh tâm tu luyện và quay lại sau **{time_str}** nữa."
                ),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Record new cooldown
        self.event_cooldowns[discord_id] = now

        # Weighted selection for events based on rarity
        weights = [e.get("weight", 25) for e in RANDOM_EVENTS]
        event = random.choices(RANDOM_EVENTS, weights=weights, k=1)[0]

        await self.bot.excel_manager.add_exp(discord_id, event["exp"])
        await self.bot.excel_manager.add_linh_thach(discord_id, event["lt"])
        await self.bot.excel_manager.add_item(discord_id, event["item"], 1)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title=f"⚡ SỰ KIỆN NGẪU NHIÊN: {event['title']}",
            description=(
                f"**{player.get('Tên')}** giáng lâm sự kiện kỳ duyên!\n\n"
                f"📜 *{event['desc']}*\n\n"
                f"🎁 **Nhận cơ duyên**:\n"
                f"• `+{event['exp']}` ✨ EXP Tu vi\n"
                f"• `+{event['lt']}` 💎 Linh Thạch\n"
                f"• `1x {event['item']}` (Đã vào Túi Đồ)\n\n"
                f"✨ Tổng EXP: `{updated_player.get('EXP')}` | 💎 Linh Thạch: `{updated_player.get('Linh thạch')}`"
            ),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))

