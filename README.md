# 📜 Hệ Thống Tu Tiên Discord Bot (Python 3.12 + discord.py + Excel + Groq AI)

Bot Discord đóng vai trò như **Hệ Thống Tu Tiên** trong các bộ truyện xuyên không/trùng sinh, tự động ghi nhận tu sĩ, quản lý cảnh giới, tu luyện, đột phá, điểm danh và trả lời thắc mắc của ký chủ bằng dữ liệu thực tế từ file Excel `data/data.xlsx` thông qua Groq AI (Llama-3.3 70B)!

---

## 🌟 Tính Năng Nổi Bật

1. **Giới Hạn Đúng 1 Kênh Discord (`CHANNEL_ID`)**:
   - Bot chỉ phản hồi trong đúng 1 kênh duy nhất được cấu hình. Các kênh khác sẽ bị bỏ qua hoàn toàn, không trả lời, không spam log.
2. **Quản Lý Dữ Liệu Bằng Excel (`data/data.xlsx`)**:
   - Tự động tạo file Excel & cấu hình các cột nếu chưa có:
     `DiscordID`, `Username`, `Tên`, `Cảnh giới`, `EXP`, `Linh thạch`, `Linh căn`, `HP`, `Mana`, `Ngày điểm danh`
   - Đảm bảo an toàn dữ liệu tuyệt đối khi nhiều người thao tác đồng thời bằng `asyncio.Lock`.
3. **Hệ Thống Lệnh Tu Tiên (Slash Commands)**:
   - `👤 /thongtin`: Xem chi tiết chỉ số tu vi, cảnh giới, linh căn.
   - `⚔️ /tu_luyen`: Bế quan tích lũy EXP ngẫu nhiên (+30~80 EXP).
   - `⬆️ /dot_pha`: Kiểm tra EXP và tiến cấp cảnh giới (Luyện Khí 1 -> Luyện Khí 2 -> ... -> Trúc Cơ -> Kim Đan -> Nguyên Anh -> Hóa Thần).
   - `🎁 /diem_danh`: Mỗi ngày điểm danh nhận +100 Linh Thạch.
   - `🏆 /top`: Bảng xếp hạng Top 10 tu sĩ có tu vi thâm hậu nhất.
   - `💰 /linhthach`: Kiểm tra túi Linh Thạch hiện có.
   - `📜 /help`: Bí kíp Thiên Cơ Các hiển thị danh sách lệnh động, phân trang thông minh với nút bấm **◀ Trước** / **Sau ▶**.
   - `🛠️ /cong_exp`, `/cong_linh_thach`, `/set_canh_gioi`: Lệnh quản trị dành cho Chưởng Môn (Admin).
4. **Hỏi Đáp Tự Nhiên Với Hệ Thống AI (Groq API)**:
   - Ký chủ nhắn tin trực tiếp trong kênh tu luyện (ví dụ: *"Ta còn bao nhiêu EXP?"*, *"Ai nhiều linh thạch nhất?"*).
   - Bot đọc file Excel, phân tích dữ liệu thực tế và đóng vai **Hệ Thống Tu Tiên** (xưng "Hệ Thống", gọi "Ký chủ", phản hồi dạng `【Hệ Thống】` hoặc `【Đinh!】`).
5. **Sẵn Sàng Triển Khai 24/7 Lên Railway**:
   - Tích hợp sẵn `railway.json`, `Procfile`, `requirements.txt`.

---

## 🛠️ Cấu Trúc Project

```
bot/
│
├── main.py              # File khởi chạy Bot Discord chính
├── config.py            # Cấu hình biến môi trường, cảnh giới, linh căn
├── excel_manager.py     # Đọc/ghi file Excel an toàn với asyncio.Lock
├── ai_handler.py        # Xử lý trí tuệ nhân tạo Groq AI đọc dữ liệu Excel
├── logger.py            # Ghi log console & log file
│
├── commands/
│   ├── info.py          # /thongtin, /linhthach, /top
│   ├── cultivation.py   # /tu_luyen, /dot_pha, /diem_danh
│   ├── admin.py        # /cong_exp, /cong_linh_thach, /set_canh_gioi
│   └── help.py         # /help động & phân trang
│
├── data/
│   └── data.xlsx        # File cơ sở dữ liệu Excel
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── railway.json
└── Procfile
```

---

## 🚀 Hướng Dẫn Chạy Cục Bộ (Local)

1. **Cài đặt Python 3.12+**
2. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình file `.env`**:
   Tạo file `.env` từ `.env.example`:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   CHANNEL_ID=123456789012345678
   GUILD_ID=123456789012345678
   GROQ_API_KEY=your_groq_api_key
   ```
4. **Bật Privileged Gateway Intents** trên [Discord Developer Portal](https://discord.com/developers/applications):
   - Bật **MESSAGE CONTENT INTENT**
   - Bật **SERVER MEMBERS INTENT**
5. **Chạy Bot**:
   ```bash
   python bot/main.py
   ```

---

## 🚆 Hướng Dẫn Triển Khai Lên Railway (24/7)

1. Đẩy code lên **GitHub** của bạn.
2. Đăng nhập [Railway.app](https://railway.app) và nhấn **New Project** ➔ **Deploy from GitHub repo**.
3. Chọn Repository vừa tạo.
4. Vào mục **Variables** trên Railway và thêm các biến môi trường:
   - `DISCORD_TOKEN` = Token Discord Bot của bạn
   - `CHANNEL_ID` = ID kênh Discord cho phép hoạt động
   - `GUILD_ID` = ID Server Discord
   - `GROQ_API_KEY` = Khóa API Groq (lấy miễn phí tại console.groq.com)
5. Railway sẽ tự động nhận diện `railway.json` và khởi chạy `python bot/main.py`.


---

## 📜 Giấy Phép
Dự án được phát hành dưới bản quyền Apache 2.0. Chúc các đệ tử tu hành đắc đạo! 🌌
