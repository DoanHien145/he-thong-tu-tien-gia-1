import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

COMMAND_EMOJIS = {
    "thongtin": "👤",
    "tu_luyen": "⚔️",
    "dot_pha": "⬆️",
    "diem_danh": "🎁",
    "top": "🏆",
    "linhthach": "💰",
    "shop": "🏪",
    "mua": "🛒",
    "nhiemvu": "📜",
    "sukien": "⚡",
    "tui_do": "🎒",
    "che_dan": "🔥",
    "dung_dan": "💊",
    "cong_exp": "🛠️",
    "cong_linh_thach": "🛠️",
    "set_canh_gioi": "🛠️",
    "help": "📖"
}

class DynamicHelpPaginator(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], author_id: int):
        super().__init__(timeout=120)
        self.pages = pages
        self.author_id = author_id
        self.current_page = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == len(self.pages) - 1)

    @discord.ui.button(label="◀ Trước", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Chỉ người gọi lệnh mới có thể thao tác!", ephemeral=True)
            return
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Sau ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Chỉ người gọi lệnh mới có thể thao tác!", ephemeral=True)
            return
        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Hiển thị bí kíp danh sách các lệnh Tông Môn")
    async def help_command(self, interaction: discord.Interaction):
        if self.bot.channel_id and interaction.channel_id != self.bot.channel_id:
            await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong kênh tông môn quy định!", ephemeral=True)
            return

        # Dynamically fetch registered application slash commands
        all_app_commands = self.bot.tree.get_commands()

        # Build list of command info
        command_list = []
        for cmd in all_app_commands:
            name = cmd.name
            desc = cmd.description or "Không có mô tả."
            emoji = COMMAND_EMOJIS.get(name, "📜")
            command_list.append({
                "name": f"{emoji} /{name}",
                "desc": desc
            })

        # Fallback list if tree commands not synced yet locally
        if not command_list:
            default_cmds = [
                ("👤 /thongtin", "Xem thông tin nhân vật tu tiên."),
                ("⚔️ /tu_luyen", "Tiến hành tu luyện để nhận EXP ngẫu nhiên."),
                ("⬆️ /dot_pha", "Thử đột phá lên cảnh giới mới nếu đủ EXP."),
                ("🎁 /diem_danh", "Điểm danh hằng ngày để nhận Linh Thạch."),
                ("🏪 /shop", "Xem Bảo Các Tông Môn — Cửa hàng Linh Đan & Nguyên Liệu."),
                ("🛒 /mua", "Mua Linh Đan hoặc Nguyên Liệu từ Bảo Các Tông Môn."),
                ("📜 /nhiemvu", "Bảng Nhiệm Vụ Hoạt Động Tông Môn — Hoàn thành để nhận thưởng!"),
                ("⚡ /sukien", "Tham gia Sự Kiện Ngẫu Nhiên Tông Môn thử vận may nhận cơ duyên."),
                ("🎒 /tui_do", "Xem Túi Đồ Linh Đan & Nguyên Liệu hiện có."),
                ("🔥 /che_dan", "Luyện chế Linh Đan từ nguyên liệu trong Túi Đồ."),
                ("💊 /dung_dan", "Sử dụng Linh Đan tăng Tu Vi / Buff Đột Phá."),
                ("🏆 /top", "Xem bảng xếp hạng tu sĩ mạnh nhất."),
                ("💰 /linhthach", "Xem số Linh Thạch hiện có."),
                ("📖 /help", "Hiển thị bí kíp danh sách các lệnh Tông Môn.")
            ]
            command_list = [{"name": c[0], "desc": c[1]} for c in default_cmds]

        # Split commands into chunks of 8 per page
        CHUNK_SIZE = 8
        chunks = [command_list[i:i + CHUNK_SIZE] for i in range(0, len(command_list), CHUNK_SIZE)]

        pages = []
        total_pages = len(chunks)

        for page_idx, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="📜 Thiên Cơ Các — Danh Sách Lệnh Tông Môn",
                description="Hệ thống bí kíp pháp bảo lệnh hỗ trợ tu sĩ:",
                color=discord.Color.from_rgb(0, 204, 153) # Xianxia Jade
            )

            for item in chunk:
                embed.add_field(
                    name=item["name"],
                    value=item["desc"],
                    inline=False
                )

            embed.add_field(
                name="────────────────────",
                value="💡 **Lưu ý**: Bot chỉ hoạt động & trả lời trong đúng kênh tông môn được chỉ định.\n💬 Bạn có thể nhắn trực tiếp câu hỏi (ví dụ: *'Ta còn bao nhiêu EXP?'*) để **Đại Lão Ẩn Mình** giải đáp!",
                inline=False
            )

            if total_pages > 1:
                embed.set_footer(text=f"Trang {page_idx + 1}/{total_pages} • Tông Môn Đại Lão Ẩn Mình")
            else:
                embed.set_footer(text="Tông Môn Đại Lão Ẩn Mình • Tiên Phong Đạo Cốt")

            pages.append(embed)

        if total_pages > 1:
            view = DynamicHelpPaginator(pages, interaction.user.id)
            await interaction.response.send_message(embed=pages[0], view=view)
        else:
            await interaction.response.send_message(embed=pages[0])

        logger.info(f"Command Executed: /help by {interaction.user.display_name}")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
