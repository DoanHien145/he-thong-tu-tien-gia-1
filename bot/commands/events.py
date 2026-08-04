import random
import asyncio
import time
import discord
from discord import app_commands
from discord.ext import commands, tasks
from bot.logger import logger
from bot.commands.economy import record_activity

# Active global active channel event state
ACTIVE_CHANNEL_EVENT = {
    "active": False,
    "title": "",
    "desc": "",
    "type": "", # "group" or "single"
    "participants": set(),
    "claimed_by": None,
    "rewards": {}
}

class GroupEventView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.bot = bot

    @discord.ui.button(label="⚡ Tham Gia Sự Kiện", style=discord.ButtonStyle.primary, emoji="🌌")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not ACTIVE_CHANNEL_EVENT["active"]:
            await interaction.response.send_message("❌ Sự kiện này đã kết thúc!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        if discord_id in ACTIVE_CHANNEL_EVENT["participants"]:
            await interaction.response.send_message("⚠️ Bạn đã đăng ký tham gia sự kiện này rồi!", ephemeral=True)
            return

        ACTIVE_CHANNEL_EVENT["participants"].add(discord_id)
        username = interaction.user.display_name
        record_activity(discord_id, "thamgia", self.bot)
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)

        # Grant immediate rewards
        await self.bot.excel_manager.get_or_create_player(discord_id, username)
        exp = ACTIVE_CHANNEL_EVENT["rewards"].get("exp", 300)
        lt = ACTIVE_CHANNEL_EVENT["rewards"].get("lt", 250)
        item = ACTIVE_CHANNEL_EVENT["rewards"].get("item", "Tam Diệp Thảo")

        await self.bot.excel_manager.add_exp(discord_id, exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, lt)
        await self.bot.excel_manager.add_item(discord_id, item, 1)

        await interaction.response.send_message(
            f"🎉 **{username}** tiến vào sự kiện **{ACTIVE_CHANNEL_EVENT['title']}**!\n"
            f"🎁 Nhận thưởng: `+{exp}` ✨ EXP | `+{lt}` 💎 Linh Thạch | `1x {item}` 🌿",
            ephemeral=False
        )

class SingleClaimView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="⚡ Nhận Cơ Duyên Ngay!", style=discord.ButtonStyle.success, emoji="🎁")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not ACTIVE_CHANNEL_EVENT["active"] or ACTIVE_CHANNEL_EVENT["claimed_by"] is not None:
            await interaction.response.send_message("❌ Cơ duyên này đã bị tu sĩ khác nhanh tay đoạt mất rồi!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        ACTIVE_CHANNEL_EVENT["claimed_by"] = username
        ACTIVE_CHANNEL_EVENT["active"] = False
        record_activity(discord_id, "nhan_co_duyen", self.bot)
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)

        self.stop()
        for child in self.children:
            child.disabled = True

        await self.bot.excel_manager.get_or_create_player(discord_id, username)
        exp = ACTIVE_CHANNEL_EVENT["rewards"].get("exp", 1000)
        lt = ACTIVE_CHANNEL_EVENT["rewards"].get("lt", 800)
        item = ACTIVE_CHANNEL_EVENT["rewards"].get("item", "Xích Viêm Quả")

        await self.bot.excel_manager.add_exp(discord_id, exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, lt)
        await self.bot.excel_manager.add_item(discord_id, item, 1)

        embed = discord.Embed(
            title="✨ CƠ DUYÊN ĐÃ CÓ CHỦ!",
            description=(
                f"🎉 **{username}** vận khí ngút trời, đã nhanh tay cướp lấy cơ duyên **{ACTIVE_CHANNEL_EVENT['title']}**!\n\n"
                f"🎁 **Phần thưởng độc quyền**:\n"
                f"• `+{exp}` ✨ EXP Tu vi\n"
                f"• `+{lt}` 💎 Linh Thạch\n"
                f"• `1x {item}` 🌿 (Cất vào Túi Đồ)"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.edit_message(embed=embed, view=self)

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.diet_quai_cooldowns: dict[str, float] = {}
        self.thu_trieu_cooldowns: dict[str, float] = {}
        self.auto_events_loop.start()

    def cog_unload(self):
        self.auto_events_loop.cancel()

    @tasks.loop(minutes=20)
    async def auto_events_loop(self):
        """Randomly broadcasts events into the configured Discord channel every 20 minutes."""
        if not self.bot.channel_id:
            return

        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.bot.channel_id)
        if not channel:
            return

        # Choose event category: 60% Group event, 40% Single-claimer Opportunity
        is_single = random.random() < 0.40

        if is_single:
            opportunities = [
                {
                    "title": "🎁 Túi Trữ Đồ Vô Chủ Giáng Lâm",
                    "desc": "Bên bờ suối tiên tỏa ánh kim quang, một chiếc túi trữ đồ của cao nhân ngàn năm lộ ra!",
                    "exp": 800, "lt": 1000, "item": "Xích Viêm Quả"
                },
                {
                    "title": "🌟 Linh Quả Mẫu Cửu Hoàn Khai Hoa",
                    "desc": "Trên đỉnh vách đá sương mù, một quả linh quả thượng phẩm vừa kết trái rực rỡ!",
                    "exp": 1200, "lt": 1500, "item": "Lôi Linh Quả"
                },
                {
                    "title": "📜 Tàn Sách Tiên Bút Xuất Hiện",
                    "desc": "Một vệt linh quang mang theo cuốn bí tịch cổ xưa rơi xuống giữa sân tông môn!",
                    "exp": 1500, "lt": 2000, "item": "Vạn Năm Linh Chi"
                },
                {
                    "title": "💎 Mạch Linh Thạch Thượng Phẩm Lộ Ra",
                    "desc": "Một vệt linh thạch phát sáng rực rỡ dưới lòng suối, chỉ 1 người duy nhất thu hoạch được!",
                    "exp": 600, "lt": 2500, "item": "Thiên Niên Tuyết Liên"
                }
            ]
            opp = random.choice(opportunities)

            ACTIVE_CHANNEL_EVENT["active"] = True
            ACTIVE_CHANNEL_EVENT["title"] = opp["title"]
            ACTIVE_CHANNEL_EVENT["desc"] = opp["desc"]
            ACTIVE_CHANNEL_EVENT["type"] = "single"
            ACTIVE_CHANNEL_EVENT["claimed_by"] = None
            ACTIVE_CHANNEL_EVENT["rewards"] = {"exp": opp["exp"], "lt": opp["lt"], "item": opp["item"]}

            view = SingleClaimView(self.bot)

            embed = discord.Embed(
                title=f"⚡ CƠ DUYÊN NGẪU NHIÊN: {opp['title']}",
                description=(
                    f"📜 *{opp['desc']}*\n\n"
                    f"⚠️ **ĐẶC BIỆT**: CHỈ **1 TU SĨ NHANH TAY NHẤT** MỚI NHẬN ĐƯỢC CƠ DUYÊN NÀY!\n"
                    f"👉 Nhấn nút bên dưới hoặc gõ `/nhan_co_duyen`!"
                ),
                color=discord.Color.gold()
            )
            await channel.send(embed=embed, view=view)
            logger.info(f"Broadcasted Single Opportunity Event: {opp['title']}")

        else:
            group_events = [
                {
                    "title": "🐾 THÚ TRIỀU BỘC PHÁT TRÀN SƠN MÔN!",
                    "desc": "Hàng ngàn hung thú từ Vạn Yêu Cốc cuồng bạo tràn xuống Sơn Môn! Triệu tập chư vị tu sĩ hợp lực chống trả Thú Triều!",
                    "exp": 2500, "lt": 1500, "item": "Vạn Năm Linh Chi"
                },
                {
                    "title": "🌌 Dị Tượng Mở Không Gian!",
                    "desc": "Một vết nứt không gian mở ra giữa bầu trời tông môn! Linh khí cuồn cuộn đổ xuống. Chư vị đồng đạo ai muốn tiến vào?",
                    "exp": 1000, "lt": 800, "item": "Tam Diệp Thảo"
                },
                {
                    "title": "🐲 Long Mạch Thức Tỉnh!",
                    "desc": "Thái cổ long mạch dưới sơn môn rung chuyển, bộc phát linh khí dạt dào!",
                    "exp": 1200, "lt": 1000, "item": "U Nhược Hoa"
                },
                {
                    "title": "🏆 Cổ Trận Linh Khí Giáng Lâm!",
                    "desc": "Trận pháp thượng cổ tự động vận hành, mở ra cơ hội hấp thu linh khí cho chư vị tu sĩ!",
                    "exp": 1500, "lt": 1200, "item": "Xích Viêm Quả"
                },
                {
                    "title": "📜 Tiên Ngự Di Bảo Xuất Hiện!",
                    "desc": "Di tích tiên nhân tỏa tiên quang chiếu sáng cả bầu trời tông môn!",
                    "exp": 2000, "lt": 1500, "item": "Lôi Linh Quả"
                }
            ]
            ge = random.choice(group_events)

            ACTIVE_CHANNEL_EVENT["active"] = True
            ACTIVE_CHANNEL_EVENT["title"] = ge["title"]
            ACTIVE_CHANNEL_EVENT["desc"] = ge["desc"]
            ACTIVE_CHANNEL_EVENT["type"] = "group"
            ACTIVE_CHANNEL_EVENT["participants"] = set()
            ACTIVE_CHANNEL_EVENT["rewards"] = {"exp": ge["exp"], "lt": ge["lt"], "item": ge["item"]}

            view = GroupEventView(self.bot)

            embed = discord.Embed(
                title=f"⛩️ BIẾN CỐ TÔNG MÔN: {ge['title']}",
                description=(
                    f"📜 *{ge['desc']}*\n\n"
                    f"✨ **Tất cả các tu sĩ** nhấn nút bên dưới hoặc gõ `/thamgia` trong vòng **2 phút** để nhận cơ duyên!"
                ),
                color=discord.Color.purple()
            )
            await channel.send(embed=embed, view=view)
            logger.info(f"Broadcasted Group Event: {ge['title']}")

    @auto_events_loop.before_loop
    async def before_auto_events(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="thamgia", description="Tham gia biến cố/sự kiện tông môn đang diễn ra")
    async def thamgia(self, interaction: discord.Interaction):
        if not ACTIVE_CHANNEL_EVENT["active"] or ACTIVE_CHANNEL_EVENT["type"] != "group":
            await interaction.response.send_message("❌ Hiện tại không có sự kiện nhóm nào đang mở!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        if discord_id in ACTIVE_CHANNEL_EVENT["participants"]:
            await interaction.response.send_message("⚠️ Bạn đã tham gia sự kiện này rồi!", ephemeral=True)
            return

        ACTIVE_CHANNEL_EVENT["participants"].add(discord_id)
        username = interaction.user.display_name
        record_activity(discord_id, "thamgia", self.bot)
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)

        await self.bot.excel_manager.get_or_create_player(discord_id, username)
        exp = ACTIVE_CHANNEL_EVENT["rewards"].get("exp", 300)
        lt = ACTIVE_CHANNEL_EVENT["rewards"].get("lt", 250)
        item = ACTIVE_CHANNEL_EVENT["rewards"].get("item", "Tam Diệp Thảo")

        await self.bot.excel_manager.add_exp(discord_id, exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, lt)
        await self.bot.excel_manager.add_item(discord_id, item, 1)

        embed = discord.Embed(
            title="✨ THAM GIA SỰ KIỆN THÀNH CÔNG!",
            description=(
                f"🎉 **{username}** đã tiến vào **{ACTIVE_CHANNEL_EVENT['title']}**!\n"
                f"🎁 Thưởng: `+{exp}` ✨ EXP | `+{lt}` 💎 Linh Thạch | `1x {item}` 🌿"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nhan_co_duyen", description="Nhanh tay nhận cơ duyên ngẫu nhiên đơn lẻ trong kênh")
    async def nhan_co_duyen(self, interaction: discord.Interaction):
        if not ACTIVE_CHANNEL_EVENT["active"] or ACTIVE_CHANNEL_EVENT["type"] != "single" or ACTIVE_CHANNEL_EVENT["claimed_by"] is not None:
            await interaction.response.send_message("❌ Không có cơ duyên nào hoặc đã bị tu sĩ khác đoạt mất!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        ACTIVE_CHANNEL_EVENT["claimed_by"] = username
        ACTIVE_CHANNEL_EVENT["active"] = False
        record_activity(discord_id, "nhan_co_duyen", self.bot)
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)

        await self.bot.excel_manager.get_or_create_player(discord_id, username)
        exp = ACTIVE_CHANNEL_EVENT["rewards"].get("exp", 1000)
        lt = ACTIVE_CHANNEL_EVENT["rewards"].get("lt", 800)
        item = ACTIVE_CHANNEL_EVENT["rewards"].get("item", "Xích Viêm Quả")

        await self.bot.excel_manager.add_exp(discord_id, exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, lt)
        await self.bot.excel_manager.add_item(discord_id, item, 1)

        embed = discord.Embed(
            title="🎁 CẮO ĐƯỢC CƠ DUYÊN NGẪU NHIÊN!",
            description=(
                f"🎉 **{username}** giáng lâm nhanh tay cướp lấy **{ACTIVE_CHANNEL_EVENT['title']}**!\n\n"
                f"🎁 **Nhận độc quyền**:\n"
                f"• `+{exp}` ✨ EXP Tu vi\n"
                f"• `+{lt}` 💎 Linh Thạch\n"
                f"• `1x {item}` 🌿 (Đã vào Túi Đồ)"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="diet_quai", description="Trảm diệt yêu quái ngẫu nhiên cản đường (Yêu cầu Tu Vi / Cảnh Giới, Cooldown 10 phút)")
    async def diet_quai(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        now = time.time()
        last = self.diet_quai_cooldowns.get(discord_id, 0)
        cooldown_time = 600  # 10 minutes max
        if now - last < cooldown_time:
            remaining = int((cooldown_time - (now - last)) / 60)
            await interaction.response.send_message(
                f"⏳ **{username}** vừa huyết chiến tiêu diệt quái gần đây! Vui lòng tĩnh dưỡng **{max(1, remaining)} phút** nữa.",
                ephemeral=True
            )
            return

        self.diet_quai_cooldowns[discord_id] = now
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)
        record_activity(discord_id, "diet_quai", self.bot)

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_realm = player.get("Cảnh giới", "Luyện Khí tầng 1")
        total_exp = int(player.get("EXP", 0))

        monsters = [
            {"name": "🐺 Cửu Trảo Yêu Lang", "min_exp": 100, "req_realm": "Luyện Khí tầng 1", "exp": 1000, "lt": 500, "item": "Tam Diệp Thảo"},
            {"name": "🕷️ Bích Nhãn Độc Nhện", "min_exp": 850, "req_realm": "Luyện Khí tầng 4", "exp": 1800, "lt": 800, "item": "U Nhược Hoa"},
            {"name": "🐻 Thạch Giáp Hùng Vương", "min_exp": 3500, "req_realm": "Luyện Khí tầng 8", "exp": 3000, "lt": 1200, "item": "Xích Viêm Quả"},
            {"name": "🐍 Xích Luyện Hỏa Xà", "min_exp": 9000, "req_realm": "Trúc Cơ Sơ Kỳ", "exp": 5000, "lt": 2000, "item": "Lôi Linh Quả"}
        ]

        monster = random.choice(monsters)

        if total_exp < monster["min_exp"]:
            embed = discord.Embed(
                title=f"💥 KHIÊU CHIẾN THẤT BẠI: {monster['name']}",
                description=(
                    f"😱 **{username}** chạm trán **{monster['name']}**!\n\n"
                    f"⚠️ Yêu quái tỏa hung khí ngút trời! Yêu cầu tu vi: **{monster['req_realm']}** (`{monster['min_exp']}` EXP).\n"
                    f"💔 Tu vi hiện tại của ngươi (`{total_exp}` EXP) chưa đủ nên bị hung thú tát văng, đành ngậm ngùi lui bước!"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Player wins
        await self.bot.excel_manager.add_exp(discord_id, monster["exp"])
        await self.bot.excel_manager.add_linh_thach(discord_id, monster["lt"])
        await self.bot.excel_manager.add_item(discord_id, monster["item"], 1)

        embed = discord.Embed(
            title=f"⚔️ DIỆT QUÁI THÀNH CÔNG: {monster['name']}",
            description=(
                f"🎉 **{username}** (`{current_realm}`) vận chuyển thần thông xuất sắc trảm diệt **{monster['name']}**!\n\n"
                f"🎁 **Phần thưởng chiến lợi phẩm**:\n"
                f"• `+{monster['exp']}` ✨ EXP Tu Vi\n"
                f"• `+{monster['lt']}` 💎 Linh Thạch\n"
                f"• `1x {monster['item']}` 🌿 (Cất vào Túi Đồ)"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="danh_thu_trieu", description="Tham gia chống trả đợt Thú Triều bộc phát bảo vệ Sơn Môn (Cooldown 10 phút)")
    async def danh_thu_trieu(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        now = time.time()
        last = self.thu_trieu_cooldowns.get(discord_id, 0)
        cooldown_time = 600  # 10 minutes (600s)
        if now - last < cooldown_time:
            remaining = int((cooldown_time - (now - last)) / 60)
            await interaction.response.send_message(
                f"⏳ **{username}** vừa tham gia chống trả Thú Triều gần đây! Vui lòng tĩnh dưỡng **{max(1, remaining)} phút** nữa.",
                ephemeral=True
            )
            return

        self.thu_trieu_cooldowns[discord_id] = now
        record_activity(discord_id, "sukien", self.bot)
        record_activity(discord_id, "su_kien", self.bot)
        record_activity(discord_id, "danh_thu_trieu", self.bot)

        await self.bot.excel_manager.get_or_create_player(discord_id, username)
        exp = random.randint(2000, 4000)
        lt = random.randint(1000, 2000)
        item = random.choice(["Xích Viêm Quả", "Lôi Linh Quả", "Vạn Năm Linh Chi"])

        await self.bot.excel_manager.add_exp(discord_id, exp)
        await self.bot.excel_manager.add_linh_thach(discord_id, lt)
        await self.bot.excel_manager.add_item(discord_id, item, 1)

        embed = discord.Embed(
            title="🐾 CHỐNG TRẢ THÚ TRIỀU THÀNH CÔNG!",
            description=(
                f"🛡️ **{username}** giáng lâm tiền tuyến, vung kiếm trảm diệt hàng trăm bầy hung thú cuồng bạo!\n\n"
                f"🎁 **Thưởng công trạng thủ thành**:\n"
                f"• `+{exp}` ✨ EXP Tu vi\n"
                f"• `+{lt}` 💎 Linh Thạch\n"
                f"• `1x {item}` 🌿 (Cất vào Túi Đồ)"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))
