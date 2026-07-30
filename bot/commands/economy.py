import random
import time
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

QUESTS = [
    {
        "id": "1",
        "name": "🌿 Hái Linh Thảo Hậu Sơn",
        "reward_lt": 50,
        "reward_exp": 30,
        "reward_item": "Tam Diệp Thảo",
        "rate": 0.95,
        "desc": "Thu hái thảo dược cơ bản cho tông môn."
    },
    {
        "id": "2",
        "name": "⚔️ Trảm Yêu Thú Ngoại Vi",
        "reward_lt": 120,
        "reward_exp": 80,
        "reward_item": "U Nhược Hoa",
        "rate": 0.85,
        "desc": "Tễ trừ yêu thú cấp thấp đe dọa đệ tử ngoại môn."
    },
    {
        "id": "3",
        "name": "🌋 Thám Hiểm Núi Lửa Thần Diệc (Hiếm)",
        "reward_lt": 250,
        "reward_exp": 150,
        "reward_item": "Xích Viêm Quả",
        "rate": 0.65,
        "desc": "Vào vùng dung nham thu thập Xích Viêm Quả quý hiếm."
    },
    {
        "id": "4",
        "name": "⚡ Truy Lùng Ma Đầu Săn Lôi Sơn (Cực Hiếm)",
        "reward_lt": 500,
        "reward_exp": 300,
        "reward_item": "Lôi Linh Quả",
        "rate": 0.45,
        "desc": "Thảo phạt ma đầu nguy hiểm trên Lôi Sơn."
    }
]

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
    }
]

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_cooldowns: dict[str, float] = {}  # discord_id -> timestamp

    @app_commands.command(name="shop", description="Xem Bảo Các Tông Môn — Cửa hàng Linh Đan & Nguyên Liệu")   {
        "title": "🎁 Túi Trữ Đồ Vô Chủ",
        "desc": "Bên bờ suối, bạn nhặt được một chiếc túi trữ đồ của cao nhân xưa để lại!",
        "exp": 250,
        "lt": 600,
        "item": "Xích Viêm Quả"
    }
]

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Xem Bảo Các Tông Môn - Cửa hàng Linh Đan & Nguyên Liệu")
    async def shop(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏪 Bảo Các Tông Môn — Cửa Hàng Tu Tiên",
            description="Sử dụng Linh Thạch 💎 để mua Linh Đan & Nguyên Liệu Chế Đan!\nDùng lệnh: `/mua [tên_vật_phẩm] [số_lượng]`",
            color=discord.Color.gold()
        )

        for name, info in SHOP_ITEMS.items():
            type_badge = "🧪 Linh Đan" if info["type"] == "dan" else "🌿 Dược Liệu"
            embed.add_field(
                name=f"{type_badge} {name} — Giá: `{info['price']}` 💎",
                value=f"└ *{info['desc']}*",
                inline=False
            )

        embed.set_footer(text="Bảo Các Tông Môn • Mua sắm uy tín, bảo đảm chất lượng")
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

        # Find exact or close match
        matched_item = None
        for item_name in SHOP_ITEMS:
            if vat_pham.strip().lower() in item_name.lower():
                matched_item = item_name
                break

        if not matched_item:
            await interaction.response.send_message(
                f"❌ Không tìm thấy vật phẩm **{vat_pham}** trong Bảo Các. Dùng `/shop` để xem danh sách!",
                ephemeral=True
            )
            return

        item_info = SHOP_ITEMS[matched_item]
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

        # Deduct cost & Add item to inventory
        await self.bot.excel_manager.add_linh_thach(discord_id, -total_cost)
        await self.bot.excel_manager.add_item(discord_id, matched_item, so_luong)

        updated_player = await self.bot.excel_manager.get_player(discord_id)

        embed = discord.Embed(
            title="🛒 Mua Sắm Thành Công!",
            description=(
                f"🎉 **{player.get('Tên')}** đã mua **{so_luong}x {matched_item}** từ Bảo Các!\n"
                f"💸 Đã thanh toán: `{total_cost}` 💎 Linh Thạch\n"
                f"💎 Linh Thạch còn lại: `{updated_player.get('Linh thạch')}` 💎\n\n"
                f"🎒 Vật phẩm đã nằm trong túi đồ! Dùng `/tui_do` để kiểm tra hoặc `/dung_dan` để sử dụng."
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nhiemvu", description="Nhận & làm nhiệm vụ Tông Môn để thu thập Linh Thạch, EXP & Dược Liệu")
    @app_commands.describe(chon_nhiem_vu="Nhập số (1-4) hoặc tên nhiệm vụ muốn thực hiện (để trống để xem danh sách)")
    async def nhiemvu(self, interaction: discord.Interaction, chon_nhiem_vu: str = ""):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name
        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)

        if not chon_nhiem_vu:
            # Show list of quests
            embed = discord.Embed(
                title="📜 Bảng Nhiệm Vụ Tông Môn",
                description="Chọn nhiệm vụ để thực hiện và nhận Linh Thạch, EXP & Dược Liệu chế đan!\nDùng lệnh: `/nhiemvu [số 1-4]`",
                color=discord.Color.blue()
            )
            for idx, q in enumerate(QUESTS, 1):
                embed.add_field(
                    name=f"Nhiệm vụ #{idx}: {q['name']}",
                    value=(
                        f"*{q['desc']}*\n"
                        f"🎁 Thưởng: `+{q['reward_lt']}` 💎 LT | `+{q['reward_exp']}` EXP | `1x {q['reward_item']}`\n"
                        f"🎯 Tỷ lệ thành công: `{int(q['rate']*100)}%`"
                    ),
                    inline=False
                )
            await interaction.response.send_message(embed=embed)
            return

        # Execute selected quest
        selected_quest = None
        cleaned_input = chon_nhiem_vu.strip()

        if cleaned_input in ["1", "2", "3", "4"]:
            idx = int(cleaned_input) - 1
            selected_quest = QUESTS[idx]
        else:
            for q in QUESTS:
                if cleaned_input.lower() in q["name"].lower():
                    selected_quest = q
                    break

        if not selected_quest:
            await interaction.response.send_message("❌ Số nhiệm vụ không hợp lệ (1-4). Gõ `/nhiemvu` để xem bảng nhiệm vụ!", ephemeral=True)
            return

        # Roll success
        is_success = random.random() <= selected_quest["rate"]

        if is_success:
            await self.bot.excel_manager.add_exp(discord_id, selected_quest["reward_exp"])
            await self.bot.excel_manager.add_linh_thach(discord_id, selected_quest["reward_lt"])
            await self.bot.excel_manager.add_item(discord_id, selected_quest["reward_item"], 1)

            updated_player = await self.bot.excel_manager.get_player(discord_id)

            embed = discord.Embed(
                title="🎉 HOÀN THÀNH NHIỆM VỤ!",
                description=(
                    f"Tu sĩ **{player.get('Tên')}** đã hoàn thành xuất sắc **{selected_quest['name']}**!\n\n"
                    f"🎁 **Phần thưởng nhận được**:\n"
                    f"• `+{selected_quest['reward_lt']}` 💎 Linh Thạch\n"
                    f"• `+{selected_quest['reward_exp']}` ✨ EXP Tu vi\n"
                    f"• `1x {selected_quest['reward_item']}` 🌿 (Thêm vào Túi Đồ)\n\n"
                    f"📊 Linh Thạch hiện tại: `{updated_player.get('Linh thạch')}` | EXP: `{updated_player.get('EXP')}`"
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="💀 NHIỆM VỤ THẤT BẠI!",
                description=(
                    f"Tu sĩ **{player.get('Tên')}** khi làm **{selected_quest['name']}** đã gặp trắc trở, yêu thú tấn công bất ngờ!\n\n"
                    f"❌ Thất bại không thu được phần thưởng. Hãy tĩnh dưỡng rồi thử lại sau!"
                ),
                color=discord.Color.red()
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
