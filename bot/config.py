import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Discord Bot Configurations
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
channel_env = os.getenv("CHANNEL_ID", "")
CHANNEL_ID = int(channel_env) if channel_env and channel_env.isdigit() and int(channel_env) > 0 else 0

guild_env = os.getenv("GUILD_ID", "")
GUILD_ID = int(guild_env) if guild_env and guild_env.isdigit() and int(guild_env) > 0 else None

# Groq / Gemini API Key for AI Answers
GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# Path to SQLite database & Excel export
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/cultivation.db")
EXCEL_PATH = os.getenv("EXCEL_PATH", "data/data.xlsx")

# Cooldown constants (in seconds)
TU_LUYEN_COOLDOWN = 60  # 1 minute
SUKIEN_COOLDOWN = 1200   # 20 minutes
SONG_TU_COOLDOWN = 1800  # 30 minutes
BOSS_ATTACK_COOLDOWN = 120 # 2 minutes

# Default Cultivation Stats for new players
DEFAULT_CANH_GIOI = "Luyện Khí tầng 1"
DEFAULT_EXP = 0
DEFAULT_LINH_THACH = 100
DEFAULT_HP = 100
DEFAULT_MANA = 100
DEFAULT_LINH_CAN = "Phàm"

# List of Cultivation Realms and required EXP to breakthrough to next level
REALMS = [
    {"name": "Luyện Khí tầng 1", "exp_required": 100},
    {"name": "Luyện Khí tầng 2", "exp_required": 250},
    {"name": "Luyện Khí tầng 3", "exp_required": 500},
    {"name": "Luyện Khí tầng 4", "exp_required": 850},
    {"name": "Luyện Khí tầng 5", "exp_required": 1300},
    {"name": "Luyện Khí tầng 6", "exp_required": 1900},
    {"name": "Luyện Khí tầng 7", "exp_required": 2600},
    {"name": "Luyện Khí tầng 8", "exp_required": 3500},
    {"name": "Luyện Khí tầng 9", "exp_required": 4500},
    {"name": "Luyện Khí Đại Viên Mãn", "exp_required": 6000},
    {"name": "Trúc Cơ Sơ Kỳ", "exp_required": 9000},
    {"name": "Trúc Cơ Trung Kỳ", "exp_required": 13000},
    {"name": "Trúc Cơ Hậu Kỳ", "exp_required": 18000},
    {"name": "Trúc Cơ Đại Viên Mãn", "exp_required": 25000},
    {"name": "Kim Đan Sơ Kỳ", "exp_required": 35000},
    {"name": "Kim Đan Trung Kỳ", "exp_required": 50000},
    {"name": "Kim Đan Hậu Kỳ", "exp_required": 70000},
    {"name": "Kim Đan Đại Viên Mãn", "exp_required": 100000},
    {"name": "Nguyên Anh Sơ Kỳ", "exp_required": 150000},
    {"name": "Nguyên Anh Trung Kỳ", "exp_required": 220000},
    {"name": "Nguyên Anh Hậu Kỳ", "exp_required": 320000},
    {"name": "Nguyên Anh Đại Viên Mãn", "exp_required": 450000},
    {"name": "Hóa Thần Sơ Kỳ", "exp_required": 650000},
    {"name": "Hóa Thần Trung Kỳ", "exp_required": 900000},
    {"name": "Hóa Thần Hậu Kỳ", "exp_required": 1300000},
    {"name": "Hóa Thần Đại Viên Mãn", "exp_required": 1800000},
    {"name": "Luyện Hư Sơ Kỳ", "exp_required": 2500000},
    {"name": "Luyện Hư Trung Kỳ", "exp_required": 3500000},
    {"name": "Luyện Hư Hậu Kỳ", "exp_required": 5000000},
    {"name": "Luyện Hư Đại Viên Mãn", "exp_required": 7000000},
    {"name": "Hợp Thể Sơ Kỳ", "exp_required": 10000000},
    {"name": "Hợp Thể Trung Kỳ", "exp_required": 15000000},
    {"name": "Hợp Thể Hậu Kỳ", "exp_required": 22000000},
    {"name": "Hợp Thể Đại Viên Mãn", "exp_required": 30000000},
    {"name": "Đại Thừa Sơ Kỳ", "exp_required": 42000000},
    {"name": "Đại Thừa Trung Kỳ", "exp_required": 60000000},
    {"name": "Đại Thừa Hậu Kỳ", "exp_required": 85000000},
    {"name": "Đại Thừa Đại Viên Mãn", "exp_required": 120000000},
    {"name": "Độ Kiếp Sơ Kỳ", "exp_required": 170000000},
    {"name": "Độ Kiếp Trung Kỳ", "exp_required": 250000000},
    {"name": "Độ Kiếp Hậu Kỳ", "exp_required": 380000000},
    {"name": "Độ Kiếp Đại Viên Mãn", "exp_required": 500000000},
    {"name": "Phàm Tiên Sơ Kỳ", "exp_required": 750000000},
    {"name": "Địa Tiên Viên Mãn", "exp_required": 1000000000},
    {"name": "Thiên Tiên Cảnh", "exp_required": 2000000000},
    {"name": "Chân Tiên Cảnh", "exp_required": 5000000000},
    {"name": "Kim Tiên Cảnh", "exp_required": 10000000000},
    {"name": "Thái Ất Kim Tiên", "exp_required": 25000000000},
    {"name": "Đại La Kim Tiên", "exp_required": 50000000000},
    {"name": "Hỗn Độn Thánh Nhân", "exp_required": 100000000000},
    {"name": "Vô Thượng Chí Tôn", "exp_required": 999999999999}
]

# Random Linh Can types for registration variety
LINH_CAN_TYPES = [
    "Phàm Linh Căn", "Kim Linh Căn", "Mộc Linh Căn", "Thủy Linh Căn",
    "Hỏa Linh Căn", "Thổ Linh Căn", "Lôi Linh Căn (Biến Dị)",
    "Băng Linh Căn (Biến Dị)", "Phong Linh Căn (Biến Dị)", "Thiên Linh Căn", "Hỗn Độn Tố Căn"
]
