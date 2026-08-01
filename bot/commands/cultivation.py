import random
import time
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from bot.config import REALMS, TU_LUYEN_COOLDOWN, SONG_TU_COOLDOWN
from bot.logger import logger
from bot.commands.economy import record_activity

class SongTuView(discord.ui.View):
    def __init__(self, requester: discord.User, target: discord.User, bot):
        super().__init__(timeout=60)
        self.requester = requester
        self.target = target
        self.bot = bot
        self.accepted = False

    @discord.ui.button(label="💖 Đồng Ý Song Tu", style=discord.ButtonStyle.success, emoji="🌸")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ Lời mời song tu này không dành cho bạn!", ephemeral=True)
            return

        self.accepted = True
        self.stop()
        for item in self.children:
            item.disabled = True

        req_id = str(self.requester.id)
        target_id = str(self.target.id)

        # Record activity for both
        record_activity(req_id, "song_tu")
        record_activity(target_id, "song_tu")

        # EXP Reward
        exp_gain = random.randint(250, 500)
        player_req, _ = await self.bot.excel_manager.add_exp(req_id, exp_gain)
        player_target, _ = await self.bot.excel_manager.add_exp(target_id, exp_gain)

        # Update partner links
        await self.bot.excel_manager.update_player(req_id, {"Song tu partner": self.target.display_name})
        await self.bot.excel_manager.update_player(target_id, {"Song tu partner": self.requester.display_name})

        embed = discord.Embed(
            title="💞 SONG TU HOÀN THÀNH — ĐẠI ĐẠO CÙNG TIẾN!",
            description=(
                f"🎉 **{self.requester.display_name}** và **{self.target.display_name}** đã nhập định song tu!\n\n"
                f"☯ Âm dương hòa hợp, linh khí thiên địa cuồn cuộn đổ vào đan điền!\n"
                f"✨ Cả 2 cùng nhận được **+{exp_gain} EXP** tu vi!\n\n"
                f"👤 **{self.requester.display_name}**: `{player_req.get('EXP')}` EXP | Cảnh giới: **{player_req.get('Cảnh giới')}**\n"
                f"👤 **{self.target.display_name}**: `{player_target.get('EXP')}` EXP | Cảnh giới: **{player_target.get('Cảnh giới')}**"
            ),
            color=discord.Color.magenta()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Từ Chối", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ Lời mời này không dành cho bạn!", ephemeral=True)
            return

        self.stop()
        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="🥀 Lời Mời Song Tu Bị Từ Chối",
            description=f"**{self.target.display_name}** đã từ chối lời mời song tu của **{self.requester.display_name}**.",
            color=discord.Color.dark_gray()
        )
        await interaction.response.edit_message(embed=embed, view=self)

class CultivationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns: dict[str, float] = {}
        self.song_tu_cooldowns: dict[str, float] = {}

    @app_commands.command(name="tu_luyen", description="Tiến hành bế quan tu luyện để nhận EXP ngẫu nhiên (Hồi chiêu 1 phút)")
    async def tu_luyen(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        # Cooldown check (60 seconds)
        now = time.time()
        last_time = self.cooldowns.get(discord_id, 0)
        if now - last_time < TU_LUYEN_COOLDOWN:
            remaining = int(TU_LUYEN_COOLDOWN - (now - last_time))
            await interaction.response.send_message(
                f"⏳ **{username}** đang vận chuyển đại chu thiên, công lực chưa hồi phục!\n"
                f"Vui lòng tĩnh tâm đợi **{remaining} giây** nữa mới có thể tiếp tục tu luyện.",
                ephemeral=True
            )
            return

        self.cooldowns[discord_id] = now
        record_activity(discord_id, "tu_luyen")

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)

        # Gain random EXP between 50 and 120
        exp_gain = random.randint(50, 120)
        updated_player, _ = await self.bot.excel_manager.add_exp(discord_id, exp_gain)

        current_realm = updated_player.get("Cảnh giới")
        total_exp = updated_player.get("EXP")

        # Check breakthrough hint
        realm_names = [r["name"] for r in REALMS]
        breakthrough_hint = ""
        if current_realm in realm_names:
            idx = realm_names.index(current_realm)
            if idx < len(REALMS) - 1:
                req_exp = REALMS[idx]["exp_required"]
                if total_exp >= req_exp:
                    breakthrough_hint = "\n⚡ *Căn cơ đã tràn đầy linh khí! Ngươi có thể dùng lệnh `/dot_pha` để đột phá Lôi Kiếp ngay!*"

        embed = discord.Embed(
            title="🧘‍♂️ Bế Quan Tu Luyện (60s CD)",
            description=(
                f"**{updated_player.get('Tên')}** hấp thụ linh khí thiên địa...\n"
                f"✨ Nhận được **+{exp_gain} EXP**!\n"
                f"📈 Tổng EXP hiện tại: `{total_exp}` EXP\n"
                f"☯ Cảnh giới hiện tại: **{current_realm}**"
                f"{breakthrough_hint}"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="song_tu", description="Mời một đồng đạo song tu cùng gia tăng tu vi vượt trội")
    @app_commands.describe(dong_dao="Chọn người chơi bạn muốn cùng song tu")
    async def song_tu(self, interaction: discord.Interaction, dong_dao: discord.Member):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        req_id = str(interaction.user.id)
        target_id = str(dong_dao.id)

        if req_id == target_id:
            await interaction.response.send_message("❌ Bạn không thể tự song tu với chính mình!", ephemeral=True)
            return

        if dong_dao.bot:
            await interaction.response.send_message("❌ Không thể song tu với Bot!", ephemeral=True)
            return

        now = time.time()
        last_req = self.song_tu_cooldowns.get(req_id, 0)
        if now - last_req < SONG_TU_COOLDOWN:
            remaining = int((SONG_TU_COOLDOWN - (now - last_req)) / 60)
            await interaction.response.send_message(
                f"⏳ Bạn vừa song tu gần đây! Vui lòng chờ **{max(1, remaining)} phút** nữa.",
                ephemeral=True
            )
            return

        self.song_tu_cooldowns[req_id] = now

        await self.bot.excel_manager.get_or_create_player(req_id, interaction.user.display_name)
        await self.bot.excel_manager.get_or_create_player(target_id, dong_dao.display_name)

        view = SongTuView(requester=interaction.user, target=dong_dao, bot=self.bot)

        embed = discord.Embed(
            title="💞 LỜI MỜI SONG TU ĐẠI ĐẠO",
            description=(
                f" Tu sĩ **{interaction.user.display_name}** đưa tay ra mời **{dong_dao.mention}** cùng tiến hành song tu!\n\n"
                f"🌸 **Song tu lợi ích**: Cả 2 cùng nhận **+250 ~ +500 EXP** tu vi khổng lồ!\n"
                f"⏱️ Lời mời sẽ tự hết hạn trong **60 giây**."
            ),
            color=discord.Color.pink()
        )
        await interaction.response.send_message(content=dong_dao.mention, embed=embed, view=view)

    @app_commands.command(name="dot_pha", description="Thử đột phá cảnh giới (Mô phỏng 3 đợt Lôi Kiếp & Nguy cơ Tâm Ma)")
    async def dot_pha(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        player = await self.bot.excel_manager.get_or_create_player(discord_id, username)
        current_realm = player.get("Cảnh giới", "Luyện Khí tầng 1")
        current_exp = int(player.get("EXP", 0))

        realm_names = [r["name"] for r in REALMS]
        idx = realm_names.index(current_realm) if current_realm in realm_names else 0

        if idx >= len(REALMS) - 1:
            embed = discord.Embed(
                title="🌌 CẢNH GIỚI TỐI CAO",
                description=f"**{player.get('Tên')}** đã đạt cảnh giới Chí Tôn **{current_realm}**!",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
            return

        req_exp = REALMS[idx]["exp_required"]
        next_realm = REALMS[idx + 1]["name"]

        if current_exp < req_exp:
            missing = req_exp - current_exp
            embed = discord.Embed(
                title="🚫 Chưa Đủ Linh Khí Đột Phá",
                description=(
                    f"Căn cơ của **{player.get('Tên')}** chưa đủ vững chắc!\n\n"
                    f"☯ Cảnh giới: **{current_realm}**\n"
                    f"✨ EXP: `{current_exp}` / `{req_exp}`\n"
                    f"❌ Còn thiếu: **{missing} EXP** để nghênh tiếp Lôi Kiếp."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Defer interaction to allow multi-step Lôi Kiếp simulation
        await interaction.response.defer()

        buff_val = int(player.get("Buff đột phá", 0))
        base_success_rate = 65 + buff_val
        success_rate = min(95, base_success_rate)

        # Initial simulation message
        embed = discord.Embed(
            title="⚡ NGHÊNH TIẾP THIÊN LÔI LÔI KIẾP ⚡",
            description=(
                f"🌩️ Mây đen ngùn ngụt phủ kín bầu trời! **{player.get('Tên')}** ngồi xếp bằng giữa lôi trận!\n"
                f"🎯 Mục tiêu: **{current_realm}**  ➔  **{next_realm}**\n"
                f"🔮 Tỷ lệ thành công: `{success_rate}%` (Buff dược liệu: +{buff_val}%)\n\n"
                f"⏳ *Thiên lôi đang tụ hội...*"
            ),
            color=discord.Color.gold()
        )
        msg = await interaction.followup.send(embed=embed)

        await asyncio.sleep(1.5)

        # Stage 1 Simulation
        embed.description = (
            f"⚡ **Thiên Lôi 1**: Tia sét bạch kim giáng thẳng xuống đỉnh đầu!\n"
            f"🛡️ **{player.get('Tên')}** vận chuyển toàn bộ công lực — **ĐỠ ĐƯỢC!**\n\n"
            f"⏳ *Đợt Lôi Kiếp thứ 2 sắp giáng xuống...*"
        )
        await msg.edit(embed=embed)
        await asyncio.sleep(1.5)

        # Stage 2 Simulation
        embed.description = (
            f"⚡ **Thiên Lôi 1**: 🛡️ Đỡ được!\n"
            f"⚡ **Thiên Lôi 2**: Hỏa Lôi rực cháy xé rách không gian!\n"
            f"🛡️ **{player.get('Tên')}** gồng mình bộc phát Linh Căn — **ĐỠ ĐƯỢC!**\n\n"
            f"⏳ *Tâm Ma xuất hiện trong đợt Lôi Kiếp cuối cùng...*"
        )
        await msg.edit(embed=embed)
        await asyncio.sleep(1.8)

        # Stage 3 Roll success / failure
        is_success = random.randint(1, 100) <= success_rate

        record_activity(discord_id, "dot_pha")

        if is_success:
            await self.bot.excel_manager.update_player(discord_id, {
                "Cảnh giới": next_realm,
                "Buff đột phá": 0
            })

            embed = discord.Embed(
                title="✨ ĐỘT PHÁ THÀNH CÔNG — THÀNH TỰU ĐẠI ĐẠO! ✨",
                description=(
                    f"⚡ **Thiên Lôi 1**: 🛡️ Đỡ được!\n"
                    f"⚡ **Thiên Lôi 2**: 🛡️ Đỡ được!\n"
                    f"⚡ **Thiên Lôi 3**: 🌟 Chấn áp Tâm Ma, hấp thụ lôi đình!\n\n"
                    f"🎉 Chúc mừng tu sĩ **{player.get('Tên')}** đã giáng hạ thiên kiếp, đột phá bước vào cảnh giới mới!\n\n"
                    f"🏆 **{current_realm}**  ➔  **{next_realm}**\n\n"
                    f"✨ EXP: `{current_exp}` | Căn cơ ngập tràn Tiên Khí!"
                ),
                color=discord.Color.green()
            )
            await msg.edit(embed=embed)
            logger.info(f"Breakthrough SUCCESS: {username} -> {next_realm}")
        else:
            # Failure outcome branches: Drop Realm OR Drop EXP OR No drop
            fail_type = random.choice(["rot_canh_gioi", "giam_exp", "that_bai_thuong"])

            if fail_type == "rot_canh_gioi" and idx > 0:
                prev_realm = REALMS[idx - 1]["name"]
                await self.bot.excel_manager.update_player(discord_id, {
                    "Cảnh giới": prev_realm,
                    "Buff đột phá": 0
                })
                embed = discord.Embed(
                    title="💥 TÂM MA QUẤY PHÁ — RỚT CẢNH GIỚI! 💥",
                    description=(
                        f"⚡ **Thiên Lôi 3**: 👺 Tâm ma thừa cơ quấy phá đan điền!\n\n"
                        f"💔 **{player.get('Tên')}** không chịu nổi lôi kiếp, đan điền bị tổn thương nghiêm trọng!\n"
                        f"⚠️ Bị **tụt 1 tiểu cảnh giới**: **{current_realm}** ➔ **{prev_realm}**!\n\n"
                        f"💡 Khuyên dùng *Tụ Khí Đan* hoặc *Tẩy Tủy Đan* tại `/shop` để tăng tỉ lệ thành công lần sau!"
                    ),
                    color=discord.Color.dark_red()
                )
            elif fail_type == "giam_exp":
                exp_loss = int(current_exp * 0.2)
                new_exp = max(0, current_exp - exp_loss)
                await self.bot.excel_manager.update_player(discord_id, {
                    "EXP": new_exp,
                    "Buff đột phá": 0
                })
                embed = discord.Embed(
                    title="💥 ĐỘT PHÁ THẤT BẠI — TỔN THẤT TU VI! 💥",
                    description=(
                        f"⚡ **Thiên Lôi 3**: 🌩️ Lôi đình chấn nứt kinh mạch!\n\n"
                        f"💔 **{player.get('Tên')}** đột phá thất bại, bị tổn thất **-{exp_loss} EXP** tu vi!\n"
                        f"📈 EXP còn lại: `{new_exp}` EXP.\n\n"
                        f"💡 Hãy bế quan `/tu_luyen` lại để phục hồi căn cơ!"
                    ),
                    color=discord.Color.red()
                )
            else:
                await self.bot.excel_manager.update_player(discord_id, {"Buff đột phá": 0})
                embed = discord.Embed(
                    title="💥 ĐỘT PHÁ THẤT BẠI 💥",
                    description=(
                        f"⚡ **Thiên Lôi 3**: 🌪️ Linh khí bộc phát tán loạn!\n\n"
                        f"💔 **{player.get('Tên')}** chưa đủ ngộ tính vượt qua lôi kiếp. Đột phá thất bại nhưng may mắn căn cơ không bị tổn hại!\n\n"
                        f"💡 Dùng đan dược trợ lực để nâng cao cơ duyên đột phá!"
                    ),
                    color=discord.Color.orange()
                )

            await msg.edit(embed=embed)
            logger.info(f"Breakthrough FAIL: {username} ({fail_type})")

    @app_commands.command(name="diem_danh", description="Điểm danh hằng ngày để nhận 150 Linh Thạch & 100 EXP & Dược Liệu")
    async def diem_danh(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        discord_id = str(interaction.user.id)
        username = interaction.user.display_name

        record_activity(discord_id, "diem_danh")
        await self.bot.excel_manager.get_or_create_player(discord_id, username)

        success, player, msg = await self.bot.excel_manager.check_in(discord_id)

        if success:
            embed = discord.Embed(
                title="🎁 Điểm Danh Tông Môn Hằng Ngày",
                description=(
                    f"**{player.get('Tên')}** đã điểm danh hôm nay!\n\n"
                    f"{msg}\n"
                    f"💎 Linh Thạch: **{player.get('Linh thạch')}** | ✨ EXP: **{player.get('EXP')}**"
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⏳ Điểm Danh Tông Môn",
                description=f"**{player.get('Tên')}**: {msg}",
                color=discord.Color.orange()
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CultivationCog(bot))
