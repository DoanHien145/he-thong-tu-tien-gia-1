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

# Groq API Key for AI Answers
GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# Path to Excel file
EXCEL_PATH = os.getenv("EXCEL_PATH", "data/data.xlsx")

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
    {"name": "Hóa Thần Hậu Kỳ", "exp_required": 1000000},
    {"name": "Luyện Hư Sơ Kỳ", "exp_required": 2000000},
    {"name": "Luyện Hư Trung Kỳ", "exp_required": 3000000},
    {"name": "Luyện Hư Hậu Kỳ", "exp_required": 4500000},
    {"name": "Luyện Hư Đại Viên Mãn", "exp_required": 6500000},

    {"name": "Hợp Thể Sơ Kỳ", "exp_required": 9000000},
    {"name": "Hợp Thể Trung Kỳ", "exp_required": 12000000},
    {"name": "Hợp Thể Hậu Kỳ", "exp_required": 16000000},
    {"name": "Hợp Thể Đại Viên Mãn", "exp_required": 21000000},

    {"name": "Đại Thừa Sơ Kỳ", "exp_required": 28000000},
    {"name": "Đại Thừa Trung Kỳ", "exp_required": 36000000},
    {"name": "Đại Thừa Hậu Kỳ", "exp_required": 46000000},
    {"name": "Đại Thừa Đại Viên Mãn", "exp_required": 58000000},

    {"name": "Độ Kiếp Sơ Kỳ", "exp_required": 72000000},
    {"name": "Độ Kiếp Trung Kỳ", "exp_required": 90000000},
    {"name": "Độ Kiếp Hậu Kỳ", "exp_required": 115000000},
    {"name": "Độ Kiếp Đại Viên Mãn", "exp_required": 145000000},

    {"name": "Bán Tiên", "exp_required": 180000000},

    {"name": "Chân Tiên Sơ Kỳ", "exp_required": 230000000},
    {"name": "Chân Tiên Trung Kỳ", "exp_required": 300000000},
    {"name": "Chân Tiên Hậu Kỳ", "exp_required": 390000000},
    {"name": "Chân Tiên Đại Viên Mãn", "exp_required": 500000000},

    {"name": "Kim Tiên", "exp_required": 650000000},
    {"name": "Thái Ất Kim Tiên", "exp_required": 850000000},
    {"name": "Đại La Kim Tiên", "exp_required": 1100000000},

    {"name": "Tiên Vương", "exp_required": 1500000000},
    {"name": "Tiên Hoàng", "exp_required": 2000000000},
    {"name": "Tiên Đế", "exp_required": 2800000000},

    {"name": "Đạo Tổ", "exp_required": 4000000000},
    {"name": "Thiên Đạo Chí Tôn", "exp_required": 6000000000},
    {"name": "Vĩnh Hằng Tiên Tôn", "exp_required": 9000000000},
    {"name": "Vô Thượng Chúa Tể", "exp_required": 13000000000},
]

# Random Linh Can types for registration variety
LINH_CAN_TYPES = [
    "Phàm Linh Căn", "Kim Linh Căn", "Mộc Linh Căn", "Thủy Linh Căn",
    "Hỏa Linh Căn", "Thổ Linh Căn", "Lôi Linh Căn (Biến Dị)",
    "Băng Linh Căn (Biến Dị)", "Phong Linh Căn (Biến Dị)", "Thiên Linh Căn", "Hỗn Độn Tố Căn"
]
