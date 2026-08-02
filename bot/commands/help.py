import discord
from discord import app_commands
from discord.ext import commands
from bot.logger import logger

COMMAND_EMOJIS = {
    "thongtin": "👤",
    "tu_luyen": "🧘‍♂️",
    "song_tu": "💖",
    "dot_pha": "⚡",
    "diem_danh": "🎁",
    "top": "🏆",
    "linhthach": "💰",
    "shop": "🏪",
    "mua": "🛒",
    "boss": "👹",
    "tancong": "⚔️",
    "nhiemvu": "📜",
    "thamgia": "🌌",
    "nhan_co_duyen": "🎁",
    "diet_quai": "⚔️",
    "danh_thu_trieu": "🐾",
    "dau_phap": "⚔️",
    "tam_bao": "🗝️",
    "tui_do": "🎒",
    "che_dan": "🔥",
    "dung_dan": "💊",
    "cong_exp": "🛠️",
    "cong_linh_thach": "🛠️",
    "set_canh_gioi": "🛠️",
    "tai_data": "📦",
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

        all_app_commands = self.bot.tree.get_commands()

        command_list = []
        for cmd in all_app_commands:
            name = cmd.name
            desc = cmd.description or "Không có mô tả."
            emoji = COMMAND_EMOJIS.get(name, "📜")
            command_list.append({
                "name": f"{emoji} /{name}",
                "desc": desc
            })

        if not command_list:
            default_cmds = [
                ("👤 /thongtin", "Xem thông tin nhân vật tu tiên."),
                ("🧘‍♂️ /tu_luyen", "Bế quan tu luyện nhận EXP (CD 1 phút)."),
                ("💖 /song_tu", "Mời đồng đạo song tu gia tăng tu vi vượt trội."),
                ("⚡ /dot_pha", "Thử đột phá Lôi Kiếp & vượt qua nguy cơ Tâm Ma."),
                ("🎁 /diem_danh", "Điểm danh hằng ngày nhận 150 Linh Thạch & Dược Liệu."),
                ("👹 /boss", "Xem thông tin Thượng Cổ Thiên Ma Boss & BXH sát thương."),
                ("⚔️ /tancong", "Tấn công Boss Thế Giới để tích lũy sát thương & linh thạch."),
                ("🏪 /shop", "Xem Bảo Các Tông Môn (Reset kho ngẫu nhiên mỗi 5p)."),
                ("🛒 /mua", "Mua Linh Đan hoặc Nguyên Liệu từ Bảo Các."),
                ("📜 /nhiemvu", "Bảng Nhiệm Vụ Hoạt Động Tông Môn."),
                ("🌌 /thamgia", "Tham gia sự kiện nhóm đang diễn ra."),
                ("🎁 /nhan_co_duyen", "Nhanh tay nhận cơ duyên đơn lẻ xuất hiện trong kênh."),
                ("🎒 /tui_do", "Xem Túi Đồ Linh Đan & Nguyên Liệu hiện có."),
                ("🔥 /che_dan", "Luyện chế Linh Đan từ nguyên liệu trong Túi Đồ."),
                ("💊 /dung_dan", "Cắn Linh Đan tăng Tu Vi / Buff Đột Phá / Hồi HP."),
                ("🏆 /top", "Xem bảng xếp hạng tu sĩ mạnh nhất."),
                ("💰 /linhthach", "Xem số Linh Thạch hiện có."),
                ("📦 /tai_data", "[Admin/Owner] Tải file dữ liệu SQLite (cultivation.db) & Excel."),
                ("📖 /help", "Hiển thị bí kíp danh sách các lệnh Tông Môn.")
            ]
            command_list = [{"name": c[0], "desc": c[1]} for c in default_cmds]

        CHUNK_SIZE = 8
        chunks = [command_list[i:i + CHUNK_SIZE] for i in range(0, len(command_list), CHUNK_SIZE)]

        pages = []
        total_pages = len(chunks)

        for page_idx, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="📜 Thiên Cơ Các — Danh Sách Lệnh Tông Môn",
                description="Hệ thống bí kíp pháp bảo lệnh hỗ trợ tu sĩ:",
                color=discord.Color.from_rgb(0, 204, 153)
            )

            for item in chunk:
                embed.add_field(
                    name=item["name"],
                    value=item["desc"],
                    inline=False
                )

            embed.add_field(
                name="────────────────────",
                value="💡 **Lưu ý**: Bot hoạt động trong đúng kênh tông môn quy định.\n💬 Bạn có thể gõ câu hỏi bắt đầu bằng dấu chấm (ví dụ: *.độ kiếp là gì*) để **Đại Lão AI** giải đáp!",
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

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
