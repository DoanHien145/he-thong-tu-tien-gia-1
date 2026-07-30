import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Discord Bot Configurations
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0")) if os.getenv("CHANNEL_ID") else 0
GUILD_ID = int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID") else None

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
    {"name": "Luyện Hư Khái Niệm", "exp_required": 2000000},
    {"name": "Độ Kiếp Thành Tiên", "exp_required": 9999999}
]

# Random Linh Can types for registration variety
LINH_CAN_TYPES = [
    "Phàm Linh Căn", "Kim Linh Căn", "Mộc Linh Căn", "Thủy Linh Căn",
    "Hỏa Linh Căn", "Thổ Linh Căn", "Lôi Linh Căn (Biến Dị)",
    "Băng Linh Căn (Biến Dị)", "Phong Linh Căn (Biến Dị)", "Thiên Linh Căn", "Hỗn Độn Tố Căn"
]
