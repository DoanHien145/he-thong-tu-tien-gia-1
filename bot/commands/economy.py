import random
import time
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from bot.config import BOSS_ATTACK_COOLDOWN, REALMS
from bot.logger import logger

SHOP_ITEMS = {
    # Linh Đan Tu Vi & Đột Phá
    "Luyện Khí Đan": {"price": 150, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Nhất Phẩm • Cắn đan nhận ngay +300 EXP tu vi"},
    "Tụ Khí Đan": {"price": 300, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Nhất Phẩm • Gia tăng +20% tỷ lệ đột phá thành công"},
    "Trúc Cơ Đan": {"price": 800, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Nhị Phẩm • Cắn đan nhận ngay +1500 EXP tu vi"},
    "Tẩy Tủy Đan": {"price": 1500, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Nhị Phẩm • Gia tăng +35% tỷ lệ đột phá thành công"},
    "Kim Đan Bảo Đan": {"price": 3500, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Tam Phẩm • Cắn đan nhận ngay +5000 EXP & +50% tỉ lệ đột phá"},
    "Nguyên Anh Đan": {"price": 8000, "type": "dan", "cat": "tu_vi", "desc": "Linh đan Tứ Phẩm • Cắn đan nhận ngay +15,000 EXP tu vi"},

    # Linh Đan Trợ Chiến & Phục Hồi
    "Hồi Xuân Đan": {"price": 500, "type": "dan", "cat": "phuc_hoi", "desc": "Linh đan Phục Hồi • Hồi phục 100 HP & 100 Mana lập tức"},
    "Thần Hành Đan": {"price": 1200, "type": "dan", "cat": "phuc_hoi", "desc": "Linh đan Trợ Chiến • Tăng tỉ lệ chấn áp Tâm Ma khi gặp lôi kiếp"},

    # Dược Liệu & Nguyên Liệu
    "Tam Diệp Thảo": {"price": 50, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Linh thảo cơ bản dùng để luyện chế Luyện Khí Đan & Tụ Khí Đan"},
    "U Nhược Hoa": {"price": 120, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Dược liệu trung cấp dùng để luyện chế Trúc Cơ Đan"},
    "Xích Viêm Quả": {"price": 300, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Linh quả hiếm dùng để luyện chế Tẩy Tủy Đan"},
    "Lôi Linh Quả": {"price": 600, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Linh quả cực hiếm hấp thụ lôi đình dùng luyện Kim Đan Bảo Đan"},
    "Vạn Năm Linh Chi": {"price": 1500, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Dược liệu thượng phẩm dùng luyện đan dược Nguyên Anh"},
    "Thiên Niên Tuyết Liên": {"price": 3000, "type": "nguyen_lieu", "cat": "duoc_lieu", "desc": "Tuyết liên ngàn năm ngưng tụ tại đỉnh núi tuyết"}
}

USER_ACTIVITIES: dict[str, set[str]] = {}
USER_QUEST_CLAIMS: dict[str, set[str]] = {}

def record_activity(discord_id: str, activity_name: str, bot=None):
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if key not in USER_ACTIVITIES:
        USER_ACTIVITIES[key] = set()
    USER_ACTIVITIES[key].add(activity_name)
    if bot and hasattr(bot, "excel_manager"):
        bot.excel_manager._sync_record_activity(discord_id, activity_name)
    else:
        try:
            from bot.excel_manager import ExcelManager
            em = ExcelManager()
            em._sync_record_activity(discord_id, activity_name)
        except Exception:
            pass

def has_activity(discord_id: str, activity_name: str, bot=None) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if activity_name in USER_ACTIVITIES.get(key, set()):
        return True
    try:
        if bot and hasattr(bot, "excel_manager"):
            return bot.excel_manager._sync_has_activity(discord_id, activity_name)
        from bot.excel_manager import ExcelManager
        em = ExcelManager()
        return em._sync_has_activity(discord_id, activity_name)
    except Exception:
        return False

def is_quest_claimed(discord_id: str, quest_id: str, bot=None) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if quest_id in USER_QUEST_CLAIMS.get(key, set()):
        return True
    if bot and hasattr(bot, "excel_manager"):
        return bot.excel_manager._sync_is_quest_claimed(discord_id, quest_id)
    return False

def mark_quest_claimed(discord_id: str, quest_id: str, bot=None):
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{discord_id}_{today}"
    if key not in USER_QUEST_CLAIMS:
        USER_QUEST_CLAIMS[key] = set()
    USER_QUEST_CLAIMS[key].add(quest_id)
    if bot and hasattr(bot, "excel_manager"):
        bot.excel_manager._sync_mark_quest_claimed(discord_id, quest_id)

QUESTS = [
    {
        "id": "1",
        "name": "📜 Siêng Năng Báo Danh",
        "activity_code": "diem_danh",
        "req_command": "/diem_danh",
        "desc": "Báo danh tông môn hàng ngày để thể hiện tinh thần mẫn cán.",
        "reward_lt": 500,
        "reward_exp": 800,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Chạy lệnh `/diem_danh` ít nhất 1 lần trong ngày!"
    },
    {
        "id": "2",
        "name": "🧘 Khổ Luyện Thành Tài",
        "activity_code": "tu_luyen",
        "req_command": "/tu_luyen",
        "desc": "Tiến hành bế quan tu luyện hấp thụ linh khí thiên địa.",
        "reward_lt": 600,
        "reward_exp": 1000,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Chạy lệnh `/tu_luyen` ít nhất 1 lần trong ngày!"
    },
    {
        "id": "3",
        "name": "💞 Song Tu Âm Dương",
        "activity_code": "song_tu",
        "req_command": "/song_tu",
        "desc": "Mời một đồng đạo cùng tiến hành song tu hòa hợp linh khí.",
        "reward_lt": 1000,
        "reward_exp": 2000,
        "reward_item": "U Nhược Hoa",
        "hint": "Chạy `/song_tu [@đồng_đạo]` và được đồng ý!"
    },
    {
        "id": "4",
        "name": "👹 Trảm Yêu Trừ Ma (Thế Giới Boss)",
        "activity_code": "tancong_boss",
        "req_command": "/tancong",
        "desc": "Tham gia tấn công Thượng Cổ Thiên Ma bảo vệ Tông Môn.",
        "reward_lt": 1500,
        "reward_exp": 2500,
        "reward_item": "Xích Viêm Quả",
        "hint": "Dùng lệnh `/tancong` để đánh Boss Thiên Ma ít nhất 1 lần!"
    },
    {
        "id": "5",
        "name": "🧪 Sơ Nhập Đan Đạo",
        "activity_code": "che_dan",
        "req_command": "/che_dan",
        "desc": "Khai mở Dược Lô luyện đan thành công.",
        "reward_lt": 800,
        "reward_exp": 1200,
        "reward_item": "U Nhược Hoa",
        "hint": "Thực hiện lệnh `/che_dan` để nhóm lửa luyện đan!"
    },
    {
        "id": "6",
        "name": "💊 Phục Dụng Linh Đan",
        "activity_code": "dung_dan",
        "req_command": "/dung_dan",
        "desc": "Sử dụng 1 viên Linh Đan bất kỳ để gia tăng công lực.",
        "reward_lt": 1000,
        "reward_exp": 1500,
        "reward_item": "Xích Viêm Quả",
        "hint": "Chạy lệnh `/dung_dan [tên_đan]` hôm nay!"
    },
    {
        "id": "7",
        "name": "🛍️ Giao Thương Bảo Các",
        "activity_code": "mua_shop",
        "req_command": "/mua",
        "desc": "Ghé thăm Bảo Các Tông Môn mua sắm đan dược hoặc dược liệu.",
        "reward_lt": 600,
        "reward_exp": 1000,
        "reward_item": "Tam Diệp Thảo",
        "hint": "Ghé `/shop` và mua bằng lệnh `/mua [tên_vật_phẩm]`!"
    },
    {
        "id": "8",
        "name": "⛩️ Thám Hiểm Bí Cảnh & Cơ Duyên",
        "activity_code": "sukien",
        "req_command": "/thamgia hoặc /nhan_co_duyen",
        "desc": "Tham gia biến cố Tông Môn hoặc cướp cơ duyên xuất hiện trong kênh.",
        "reward_lt": 1200,
        "reward_exp": 2000,
        "reward_item": "Lôi Linh Quả",
        "hint": "Nhấn nút hoặc gõ `/thamgia` / `/nhan_co_duyen` khi sự kiện xuất hiện!"
    }
]

def check_quest_condition(discord_id: str, quest: dict, player: dict, inventory: dict, bot=None) -> tuple[bool, str]:
    code = quest["activity_code"]
    today = datetime.now().strftime("%Y-%m-%d")

    if code == "diem_danh":
        if player.get("Ngày điểm danh") == today or has_activity(discord_id, "diem_danh", bot):
            return True, "Đã báo danh thành công!"
        return False, "Bạn chưa báo danh hôm nay. Hãy chạy lệnh `/diem_danh` trước!"

    if code == "tu_luyen":
        if has_activity(discord_id, "tu_luyen", bot) or has_activity(discord_id, "tu_luyen_thanh_cong", bot):
            return True, "Đã hoàn thành tu luyện hôm nay!"
        return False, "Bạn chưa bế quan tu luyện hôm nay. Hãy chạy lệnh `/tu_luyen` trước!"

    if code == "song_tu":
        if has_activity(discord_id, "song_tu", bot):
            return True, "Đã hoàn thành song tu hôm nay!"
        return False, "Bạn chưa thực hiện song tu hôm nay. Hãy dùng `/song_tu [@đồng_đạo]`!"

    if code == "tancong_boss":
        has_boss_hit = False
        if bot and hasattr(bot, "excel_manager"):
            try:
                has_boss_hit = bot.excel_manager._sync_has_boss_damage(discord_id)
            except Exception:
                pass
        if has_boss_hit or any(has_activity(discord_id, act, bot) for act in ["tancong_boss", "tancong", "danh_boss"]):
            return True, "Đã tấn công Thượng Cổ Thiên Ma hôm nay!"
        return False, "Bạn chưa tấn công Boss hôm nay. Hãy dùng lệnh `/tancong`!"

    if code == "che_dan":
        if has_activity(discord_id, "che_dan", bot):
            return True, "Đã mở lò luyện đan hôm nay!"
        return False, "Bạn chưa luyện đan hôm nay. Hãy dùng lệnh `/che_dan`!"

    if code == "dung_dan":
        if has_activity(discord_id, "dung_dan", bot):
            return True, "Đã cắn đan dược hôm nay!"
        return False, "Bạn chưa sử dụng linh đan hôm nay. Hãy dùng lệnh `/dung_dan [tên_đan]` trước!"

    if code in ["mua_shop", "mua_hang"]:
        if any(has_activity(discord_id, act, bot) for act in ["mua_shop", "mua_hang", "mua"]):
            return True, "Đã giao dịch mua hàng tại Bảo Các!"
        return False, "Bạn chưa mua hàng tại Bảo Các. Hãy xem `/shop` và mua bằng `/mua [tên_vật_phẩm]`!"

    if code in ["sukien", "su_kien"]:
        if any(has_activity(discord_id, act, bot) for act in ["sukien", "su_kien", "thamgia", "nhan_co_duyen", "danh_thu_trieu", "diet_quai"]):
            return True, "Đã tham gia sự kiện Tông Môn / nhận cơ duyên!"
        return False, "Bạn chưa tham gia sự kiện Tông Môn nào hôm nay!"

    return False, "Chưa hoàn thành điều kiện."

async def claim_all_quests_for_user(bot, discord_id: str, username: str) -> tuple[discord.Embed, int]:
    """Claims all completed and unclaimed quests for a given user at once."""
    player = await bot.excel_manager.get_or_create_player(discord_id, username)
    inventory = await bot.excel_manager.get_inventory(discord_id)

    ready_quests = []
    for q in QUESTS:
        if not is_quest_claimed(discord_id, q["id"], bot):
            ok, _ = check_quest_condition(discord_id, q, player, inventory, bot)
            if ok:
                ready_quests.append(q)

    if not ready_quests:
        embed = discord.Embed(
            title="📜 Không Có Nhiệm Vụ Nào Chờ Nhận",
            description=(
                f"Tu sĩ **{player.get('Tên')}** chưa có nhiệm vụ nào đủ điều kiện hoặc đã nhận hết tất cả thưởng hôm nay rồi!\n\n"
                f"👉 **Hướng dẫn thực hiện các nhiệm vụ hôm nay**:\n"
                f"• `/diem_danh` — Báo danh nhận Linh Thạch & EXP\n"
                f"• `/tu_luyen` — Bế quan tu luyện linh khí\n"
                f"• `/song_tu` — Mời đồng đạo song tu hòa hợp\n"
                f"• `/tancong` — Tấn công Boss Thượng Cổ Thiên Ma\n"
                f"• `/che_dan` — Khai mở Dược Lô luyện đan\n"
                f"• `/dung_dan` — Sử dụng 1 viên Linh Đan\n"
                f"• `/mua` — Mua hàng tại Bảo Các Tông Môn\n"
                f"• `/thamgia` / `/nhan_co_duyen` — Tham gia sự kiện Tông Môn"
            ),
            color=discord.Color.orange()
        )
        return embed, 0

    total_lt = 0
    total_exp = 0
    items_added = {}
    claimed_lines = []

    for q in ready_quests:
        mark_quest_claimed(discord_id, q["id"], bot)
        total_lt += q["reward_lt"]
        total_exp += q["reward_exp"]
        item = q["reward_item"]
        items_added[item] = items_added.get(item, 0) + 1
        claimed_lines.append(f"✅ **{q['name']}**: `+{q['reward_lt']}` 💎 LT | `+{q['reward_exp']}` ✨ EXP | `1x {item}` 🌿")

    # Update player stats & inventory
    await bot.excel_manager.add_exp(discord_id, total_exp)
    await bot.excel_manager.add_linh_thach(discord_id, total_lt)
    for item, qty in items_added.items():
        await bot.excel_manager.add_item(discord_id, item, qty)

    updated_player = await bot.excel_manager.get_player(discord_id)
    items_str = ", ".join([f"`{qty}x {item}`" for item, qty in items_added.items()])

    embed = discord.Embed(
        title=f"🎉 TỰ ĐỘNG NHẬN TẤT CẢ THƯỞNG ({len(ready_quests)} NHIỆM VỤ)!",
        description=(
            f"Tu sĩ **{player.get('Tên')}** đã hoàn tất & nhận trọn bộ phần thưởng **{len(ready_quests)} nhiệm vụ**:\n\n"
            + "\n".join(claimed_lines) + "\n\n"
            f"🎁 **TỔNG CỘNG PHẦN THƯỞNG**:\n"
            f"• `+{total_lt:,}` 💎 Linh Thạch\n"
            f"• `+{total_exp:,}` ✨ EXP Tu vi\n"
            f"• Vật phẩm: {items_str} 🌿 (Đã chuyển vào Túi Đồ)\n\n"
            f"📊 Linh Thạch hiện tại: `{updated_player.get('Linh thạch'):,}` 💎 | EXP: `{updated_player.get('EXP'):,}` ✨"
        ),
        color=discord.Color.green()
    )
    return embed, len(ready_quests)

class NhanTatCaNhiemVuView(discord.ui.View):
    def __init__(self, bot, author_id: str):
        super().__init__(timeout=120)
        self.bot = bot
        self.author_id = str(author_id)

    @discord.ui.button(label="🎁 Nhận Tất Cả Thưởng Nhiệm Vụ", style=discord.ButtonStyle.success, emoji="📜")
    async def claim_all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.author_id:
            await interaction.response.send_message("❌ Lệnh này chỉ dành cho tu sĩ đã mở bảng nhiệm vụ!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        embed, claimed_count = await claim_all_quests_for_user(self.bot, discord_id, username)

        if claimed_count > 0:
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boss_cooldowns: dict[str, float] = {}
        self.shop_last_refresh: float = 0
        self.shop_stock: dict[str, dict] = {}
        self.user_purchases: dict[str, dict[str, int]] = {}

    def refresh_shop_if_needed(self):
        now = time.time()
        # Reset shop every 5 minutes (300 seconds)
        if now - self.shop_last_refresh >= 300 or not self.shop_stock:
            self.shop_last_refresh = now
            self.shop_stock = {}
            self.user_purchases = {}
            all_items = list(SHOP_ITEMS.items())
            num_items = random.randint(6, min(10, len(all_items)))
            chosen_items = random.sample(all_items, num_items)

            for name, info in chosen_items:
                stock_qty = random.randint(3, 12)
                self.shop_stock[name] = {
                    "price": info["price"],
                    "stock": stock_qty,
                    "max_stock": stock_qty,
                    "type": info["type"],
                    "cat": info["cat"],
                    "desc": info["desc"]
                }

    def get_time_until_reset(self) -> str:
        now = time.time()
        remaining = max(0, int(300 - (now - self.shop_last_refresh)))
        m, s = divmod(remaining, 60)
        return f"{m}m {s}s"

    @app_commands.command(name="shop", description="Xem Bảo Các Tông Môn — Cửa hàng Linh Đan & Nguyên Liệu (Thiết kế mới dễ nhìn)")
    async def shop(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        self.refresh_shop_if_needed()
        reset_time = self.get_time_until_reset()
        user_bought_map = self.user_purchases.get(discord_id, {})

        embed = discord.Embed(
            title="🏪 BẢO CÁC TÔNG MÔN — KHO VẬT PHẨM VẬN MAY",
            description=(
                "✨ **Bảo Các vừa nhập đợt hàng mới!**\n"
                "🔒 **Quy định**: Mỗi tu sĩ chỉ mua **tối đa 2 cái/món** mỗi đợt 5 phút.\n"
                "💎 **Mua hàng**: `/mua [tên_vật_phẩm] [số_lượng]`\n"
                f"⏱️ **Đổi đợt hàng sau**: `{reset_time}`"
            ),
            color=discord.Color.gold()
        )

        categories = {
            "tu_vi": "🧪 LINH ĐAN TU VI & ĐỘT PHÁ",
            "phuc_hoi": "💊 LINH ĐAN TRỢ CHIẾN & PHỤC HỒI",
            "duoc_lieu": "🌿 DƯỢC LIỆU & NGUYÊN LIỆU"
        }

        for cat_key, cat_title in categories.items():
            cat_items = {k: v for k, v in self.shop_stock.items() if v.get("cat") == cat_key}
            if not cat_items:
                continue

            lines = []
            for name, info in cat_items.items():
                bought_cnt = user_bought_map.get(name, 0)
                user_limit = min(2, info["max_stock"])
                stock_str = f"`{info['stock']}/{info['max_stock']}`" if info['stock'] > 0 else "❌ **HẾT HÀNG**"
                lines.append(
                    f"🔹 **{name}** — Giá: `{info['price']}` 💎\n"
                    f"└ *{info['desc']}*\n"
                    f"└ Kho tổng: {stock_str} | 👤 Đã mua: `{bought_cnt}/{user_limit}`"
                )

            embed.add_field(
                name=f"━━━ {cat_title} ━━━",
                value="\n\n".join(lines),
                inline=False
            )

        embed.set_footer(text=f"Bảo Các Tông Môn • Tự làm mới kho ngẫu nhiên mỗi 5 phút (Còn: {reset_time})")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mua", description="Mua Linh Đan hoặc Nguyên Liệu từ Bảo Các Tông Môn")
    @app_commands.describe(vat_pham="Tên vật phẩm", so_luong="Số lượng mua")
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
                f"❌ Bảo Các hiện không bán vật phẩm **{vat_pham}** trong đợt này!\n"
                f"Dùng `/shop` để xem các món đang bán. Đợt hàng mới về sau `{reset_time}`.",
                ephemeral=True
            )
            return

        item_info = self.shop_stock[matched_item]
        available_stock = item_info["stock"]

        if available_stock <= 0:
            await interaction.response.send_message(
                f"❌ Vật phẩm **{matched_item}** đã hết hàng đợt này! Vui lòng chờ đợt sau `{reset_time}`.",
                ephemeral=True
            )
            return

        user_bought_map = self.user_purchases.setdefault(discord_id, {})
        already_bought = user_bought_map.get(matched_item, 0)
        per_user_max = min(2, item_info["max_stock"])

        if already_bought >= per_user_max:
            await interaction.response.send_message(
                f"❌ Bạn đã đạt giới hạn mua tối đa (**{per_user_max}x {matched_item}**) đợt này! Vui lòng chờ reset sau `{reset_time}`.",
                ephemeral=True
            )
            return

        if already_bought + so_luong > per_user_max:
            can_buy_more = per_user_max - already_bought
            await interaction.response.send_message(
                f"❌ Bạn chỉ được mua thêm tối đa **{can_buy_more}x {matched_item}** nữa trong đợt này!",
                ephemeral=True
            )
            return

        if so_luong > available_stock:
            await interaction.response.send_message(
                f"❌ Kho Bảo Các hiện chỉ còn **{available_stock}x {matched_item}**!",
                ephemeral=True
            )
            return

        total_cost = item_info["price"] * so_luong
        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_lt = int(player.get("Linh thạch") or 0)

        if current_lt < total_cost:
            embed = discord.Embed(
                title="💸 Linh Thạch Không Đủ",
                description=(
                    f"**{player.get('Tên')}** muốn mua **{so_luong}x {matched_item}**!\n"
                    f"💰 Chi phí: `{total_cost}` Linh Thạch | Bạn có: `{current_lt}` Linh Thạch\n"
                    f"❌ Còn thiếu: `{total_cost - current_lt}` 💎"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        record_activity(discord_id, "mua_shop", self.bot)
        record_activity(discord_id, "mua_hang", self.bot)
        record_activity(discord_id, "mua", self.bot)

        self.shop_stock[matched_item]["stock"] -= so_luong
        user_bought_map[matched_item] = already_bought + so_luong

        await self.bot.excel_manager.add_linh_thach(discord_id, -total_cost)
        await self.bot.excel_manager.add_item(discord_id, matched_item, so_luong)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title="🛒 Mua Sắm Thành Công!",
            description=(
                f"🎉 **{player.get('Tên')}** đã mua **{so_luong}x {matched_item}**!\n"
                f"💸 Đã trả: `{total_cost}` 💎 Linh Thạch\n"
                f"💎 Linh thạch còn lại: `{updated_player.get('Linh thạch')}` 💎\n"
                f"🎒 Đã thêm vào `/tui_do`!"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    # --- WORLD BOSS SYSTEM ---
    @app_commands.command(name="boss", description="Xem thông tin Thượng Cổ Thiên Ma Boss & Bảng Xếp Hạng Sát Thương")
    async def boss(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        boss_info = await self.bot.excel_manager.get_daily_boss()
        leaderboard = await self.bot.excel_manager.get_boss_leaderboard(limit=5)

        hp_pct = max(0, int((boss_info['hp'] / boss_info['max_hp']) * 100))
        bar_len = 12
        filled = int((hp_pct / 100) * bar_len)
        health_bar = "█" * filled + "░" * (bar_len - filled)

        status_str = "🟢 ĐANG XUẤT HIỆN" if boss_info["is_dead"] == 0 else "☠️ ĐÃ BỊ TIÊU DIỆT"

        embed = discord.Embed(
            title=f"👹 THẾ GIỚI BOSS: {boss_info['name']}",
            description=(
                f"Trạng thái: **{status_str}**\n"
                f"❤️ Sinh lực: `[{health_bar}]` **{boss_info['hp']:,} / {boss_info['max_hp']:,} HP** ({hp_pct}%)\n\n"
                f"⚔️ Sử dụng lệnh `/tancong` để tấn công Boss nhận linh thạch & EXP!"
            ),
            color=discord.Color.dark_red()
        )

        if leaderboard:
            lb_lines = []
            for i, entry in enumerate(leaderboard, 1):
                icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
                lb_lines.append(f"{icon} Top {i}: **{entry['name']}** — `{entry['damage']:,}` Sát thương")
            embed.add_field(name="🏆 BANG XẾP HẠNG SÁT THƯƠNG HÔM NAY", value="\n".join(lb_lines), inline=False)
        else:
            embed.add_field(name="🏆 BẢNG XẾP HẠNG SÁT THƯƠNG", value="*Chưa có tu sĩ nào tấn công Boss hôm nay.*", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tancong", description="Tấn công Thượng Cổ Thiên Ma Boss (Sát thương tùy thuộc Cảnh Giới, Cooldown 2p)")
    async def tancong(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        now = time.time()
        last_attack = self.boss_cooldowns.get(discord_id, 0)
        if now - last_attack < BOSS_ATTACK_COOLDOWN:
            remaining = int(BOSS_ATTACK_COOLDOWN - (now - last_attack))
            await interaction.response.send_message(
                f"⏳ Công lực của **{username}** chưa chấn định! Vui lòng chờ **{remaining} giây** nữa.",
                ephemeral=True
            )
            return

        boss_info = await self.bot.excel_manager.get_daily_boss()
        if boss_info["is_dead"] == 1:
            await interaction.response.send_message(
                f"☠️ **{boss_info['name']}** đã bị chư vị đồng đạo tiêu diệt hôm nay! Hãy quay lại vào ngày mai.",
                ephemeral=True
            )
            return

        self.boss_cooldowns[discord_id] = now
        record_activity(discord_id, "tancong_boss", self.bot)
        record_activity(discord_id, "tancong", self.bot)
        record_activity(discord_id, "danh_boss", self.bot)

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_realm = player.get("Cảnh giới", "Luyện Khí tầng 1")

        # Calculate damage multiplier based on Realm index
        realm_names = [r["name"] for r in REALMS]
        idx = realm_names.index(current_realm) if current_realm in realm_names else 0

        base_dmg = random.randint(200, 500)
        multiplier = 1.0 + (idx * 0.8)
        damage = int(base_dmg * multiplier)

        updated_boss, killed = await self.bot.excel_manager.attack_daily_boss(discord_id, username, damage)

        # Rewards for attacking
        reward_lt = random.randint(300, 800) + (idx * 100)
        reward_exp = random.randint(800, 2000) + (idx * 150)

        await self.bot.excel_manager.add_exp(discord_id, reward_exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, reward_lt)

        embed = discord.Embed(
            title=f"⚔️ TẤN CÔNG BOSS THIÊN MA! ⚔️",
            description=(
                f"💥 **{username}** (`{current_realm}`) giáng công kích thần thông vào **{boss_info['name']}**!\n"
                f"🔥 Gây ra **{damage:,} Sát Thương**!\n"
                f"❤️ Sinh lực Boss: **366,769 / 366,769 HP** (Bất Tử — Đã cộng dồn sát thương vào Bảng Xếp Hạng!)\n\n"
                f"🎁 **Thưởng tham chiến**: `+{reward_lt}` 💎 Linh Thạch | `+{reward_exp}` ✨ EXP"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nhiemvu", description="Bảng Nhiệm Vụ Hoạt Động Tông Môn — Hoàn thành để tự động nhận tất cả thưởng!")
    @app_commands.describe(chon_nhiem_vu="Nhập số (1-8) để nhận 1 cái, hoặc để trống / gõ 'all' để tự động gom TẤT CẢ thưởng đã hoàn thành")
    async def nhiemvu(self, interaction: discord.Interaction, chon_nhiem_vu: str = ""):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name
        cleaned_input = chon_nhiem_vu.strip().lower()

        # If empty or explicitly asking for all ("all", "tat_ca", "0", etc.):
        if not cleaned_input or cleaned_input in ["all", "tat_ca", "nhan_tat_ca", "0", "tất cả", "nhận tất cả"]:
            # Automatically claim all completed & unclaimed quests at once
            embed, claimed_count = await claim_all_quests_for_user(self.bot, discord_id, username)

            if claimed_count > 0:
                # Successfully claimed 1 or more completed quests!
                await interaction.response.send_message(embed=embed)
                return

            # If no unclaimed completed quests were ready, display the full Quest Board Embed along with interactive "Nhận Tất Cả" button
            player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
            inventory = await self.bot.excel_manager.get_inventory(discord_id)

            board_embed = discord.Embed(
                title="📜 BẢNG NHIỆM VỤ HOẠT ĐỘNG TÔNG MÔN",
                description=(
                    f"Chào tu sĩ **{player.get('Tên')}**! Hoàn thành hoạt động hàng ngày để nhận thưởng.\n"
                    f"👉 **Mẹo**: Khi làm xong hoạt động, gõ `/nhiemvu` hoặc bấm nút **[🎁 Nhận Tất Cả Thưởng]** bên dưới để gom toàn bộ phần thưởng cùng lúc!"
                ),
                color=discord.Color.blue()
            )

            for idx, q in enumerate(QUESTS, 1):
                claimed = is_quest_claimed(discord_id, q["id"], self.bot)
                ok, note = check_quest_condition(discord_id, q, player, inventory, self.bot)

                if claimed:
                    status = "🟢 `[ĐÃ HOÀN THÀNH HÔM NAY]`"
                elif ok:
                    status = f"✨ `[ĐÃ ĐỦ ĐIỀU KIỆN — Gõ /nhiemvu {idx} hoặc bấm Nhận Tất Cả]`"
                else:
                    status = f"🔒 `[CHƯA HOÀN THÀNH — {q['req_command']}]`"

                board_embed.add_field(
                    name=f"Nhiệm vụ #{idx}: {q['name']} — {status}",
                    value=(
                        f"└ *{q['desc']}*\n"
                        f"└ 🎯 **Yêu cầu**: `{q['req_command']}`\n"
                        f"└ 🎁 **Thưởng**: `+{q['reward_lt']}` 💎 LT | `+{q['reward_exp']}` ✨ EXP | `1x {q['reward_item']}` 🌿"
                    ),
                    inline=False
                )

            board_embed.set_footer(text="Nhiệm vụ tông môn tự động reset hàng ngày!")
            view = NhanTatCaNhiemVuView(self.bot, discord_id)
            await interaction.response.send_message(embed=board_embed, view=view)
            return

        # Execute / claim single selected quest (e.g. /nhiemvu 3)
        selected_quest = None
        if cleaned_input in [str(i) for i in range(1, len(QUESTS) + 1)]:
            idx = int(cleaned_input) - 1
            selected_quest = QUESTS[idx]

        if not selected_quest:
            await interaction.response.send_message(
                f"❌ Số nhiệm vụ không hợp lệ (1-{len(QUESTS)}). Gõ `/nhiemvu` để tự động nhận tất cả hoặc xem bảng nhiệm vụ!",
                ephemeral=True
            )
            return

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        inventory = await self.bot.excel_manager.get_inventory(discord_id)

        if is_quest_claimed(discord_id, selected_quest["id"], self.bot):
            embed = discord.Embed(
                title="✅ Đã Nhận Thưởng Hôm Nay",
                description=f"Tu sĩ **{player.get('Tên')}** đã nhận thưởng nhiệm vụ **{selected_quest['name']}** rồi!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ok, reason = check_quest_condition(discord_id, selected_quest, player, inventory, self.bot)
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

        mark_quest_claimed(discord_id, selected_quest["id"], self.bot)
        await self.bot.excel_manager.add_exp(discord_id, selected_quest["reward_exp"])
        await self.bot.excel_manager.add_linh_thach(discord_id, selected_quest["reward_lt"])
        await self.bot.excel_manager.add_item(discord_id, selected_quest["reward_item"], 1)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title="🎉 HOÀN THÀNH NHIỆM VỤ TÔNG MÔN!",
            description=(
                f"Tu sĩ **{player.get('Tên')}** đã hoàn tất nhiệm vụ **{selected_quest['name']}**!\n\n"
                f"🎁 **Phần thưởng**:\n"
                f"• `+{selected_quest['reward_lt']}` 💎 Linh Thạch\n"
                f"• `+{selected_quest['reward_exp']}` ✨ EXP Tu vi\n"
                f"• `1x {selected_quest['reward_item']}` 🌿 (Đã vào Túi Đồ)\n\n"
                f"📊 Linh Thạch hiện tại: `{updated_player.get('Linh thạch'):,}` 💎 | EXP: `{updated_player.get('EXP'):,}` ✨"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
