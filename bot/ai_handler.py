import json
from groq import AsyncGroq
from bot.config import GROQ_API_KEY, REALMS
from bot.logger import logger

SYSTEM_PROMPT = """
Bạn là 'Hệ Thống Tu Tiên' (System) hỗ trợ người chơi tu luyện trong thế giới huyền huyễn, tiên hiệp.
VAI TRÒ VÀ VĂN PHONG:
- Lập trường: Là một Hệ Thống vô cảm, khách quan nhưng lịch sự và hỗ trợ ký chủ hết lòng.
- Tuyệt đối KHÔNG xưng là AI, ChatGPT, OpenAI hay con người, không xưng 'Tôi', 'Lão phu' hay 'Đại Lão'.
- Tự xưng: 'Hệ Thống', 'Bổn Hệ Thống', hoặc 'Hệ Thống Tu Tiên'.
- Gọi người chơi: 'Ký chủ', 'Đạo hữu', 'Người tu luyện', hoặc 'Chủ nhân'.
- Định dạng bắt đầu: Mọi câu trả lời BẮT ĐẦU BẰNG "【Hệ Thống】" hoặc "【Đinh!】" (khi có phần thưởng, đột phá hoặc thành tựu).
- Văn phong: Ngắn gọn, rõ ràng, dạng thông báo hệ thống hoặc bảng trạng thái tu tiên.

QUY TẮC TRẢ LỜI:
1. Luôn dựa trên DỮ LIỆU EXCEL TÔNG MÔN.
2. Tuyệt đối KHÔNG tự bịa ra thông tin không có trong Excel.
3. Nếu không có dữ liệu về người chơi trong Excel, trả lời chính xác:
【Hệ Thống】

Không tìm thấy thông tin của ký chủ.
4. Nếu câu hỏi ngoài phạm vi dữ liệu Excel:
【Hệ Thống】

Không có dữ liệu liên quan trong cơ sở dữ liệu của Hệ Thống.
"""

class AIHandler:
    def __init__(self, api_key: str = GROQ_API_KEY):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            try:
                self.client = AsyncGroq(api_key=self.api_key)
                logger.info("AIHandler: Initialized Groq client successfully.")
            except Exception as e:
                logger.warning(f"AIHandler: Failed to initialize Groq client ({e}). Will use fallback parser.")

    async def answer_question(
        self,
        question: str,
        user_discord_id: str,
        user_display_name: str,
        excel_data: list[dict]
    ) -> str:
        """
        Processes user query using Groq API (Llama-3.3 70B) with Excel data context.
        """
        # Find active asking user in excel
        asking_user_data = None
        for p in excel_data:
            if str(p.get("DiscordID")) == str(user_discord_id):
                asking_user_data = p
                break

        # Calculate breakthrough needs for asking user
        need_exp_info = ""
        if asking_user_data:
            current_realm = asking_user_data.get("Cảnh giới", "")
            current_exp = int(asking_user_data.get("EXP", 0))
            realm_names = [r["name"] for r in REALMS]
            if current_realm in realm_names:
                idx = realm_names.index(current_realm)
                req_exp = REALMS[idx]["exp_required"]
                missing_exp = max(0, req_exp - current_exp)
                next_realm = REALMS[idx + 1]["name"] if idx + 1 < len(REALMS) else "Cảnh giới tối cao"
                need_exp_info = f"Ghi chú đột phá cho {asking_user_data.get('Tên')}: Đang ở {current_realm} ({current_exp} EXP). Cần {req_exp} EXP để lên {next_realm} (Còn thiếu {missing_exp} EXP)."

        # Context JSON
        context_data = {
            "Nguoi_Dang_Hoi": {
                "DiscordID": str(user_discord_id),
                "Ten_Discord": user_display_name,
                "Thong_Tin_Trong_Excel": asking_user_data
            },
            "Thong_Tin_Dot_Pha_Calculated": need_exp_info,
            "Danh_Sach_Tua_Si_Excel": excel_data
        }

        prompt = f"""
[DỮ LIỆU EXCEL TÔNG MÔN MOI NHẤT]:
{json.dumps(context_data, ensure_ascii=False, indent=2)}

[CÂU HỎI CỦA KÝ CHỦ ({user_display_name})]:
"{question}"
"""

        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2
                )
                if response and response.choices and response.choices[0].message.content:
                    logger.info(f"AI Response generated for user {user_display_name}")
                    return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Error calling Groq API: {e}")

        # Fallback if Groq unavailable or failed
        return self._rule_based_fallback(question, asking_user_data, excel_data, need_exp_info)

    def _rule_based_fallback(
        self,
        question: str,
        user_data: dict | None,
        all_players: list[dict],
        need_exp_info: str
    ) -> str:
        q = question.lower()

        if "bao nhiêu exp" in q or "kinh nghiệm" in q or "exp" in q:
            if user_data:
                return f"【Hệ Thống】\n\nKý chủ **{user_data.get('Tên')}** hiện có:\n{user_data.get('EXP')} EXP\n\n{need_exp_info}"
            return "【Hệ Thống】\n\nKhông tìm thấy thông tin của ký chủ."

        if "cảnh giới" in q or "đang ở đâu" in q:
            if user_data:
                return f"【Hệ Thống】\n\nTrạng thái ký chủ **{user_data.get('Tên')}**:\n- Cảnh giới: {user_data.get('Cảnh giới')}\n- Linh căn: {user_data.get('Linh căn')}"

        if "linh thạch" in q or "tiền" in q:
            if user_data:
                return f"【Hệ Thống】\n\nSố dư Linh Thạch của ký chủ **{user_data.get('Tên')}**:\n+ {user_data.get('Linh thạch')} Linh Thạch"

        if "mạnh nhất" in q or "top" in q or "cao nhất" in q:
            if all_players:
                realm_names = [r["name"] for r in REALMS]
                top_p = sorted(
                    all_players,
                    key=lambda p: (
                        realm_names.index(p.get("Cảnh giới")) if p.get("Cảnh giới") in realm_names else -1,
                        int(p.get("EXP", 0))
                    ),
                    reverse=True
                )[0]
                return f"【Hệ Thống】\n\nTu sĩ tu vi cao nhất Tông Môn:\n- Ký chủ: {top_p.get('Tên')}\n- Cảnh giới: {top_p.get('Cảnh giới')}\n- EXP: {top_p.get('EXP')}"

        if user_data:
            return f"【Hệ Thống】\n\nKý chủ **{user_data.get('Tên')}** ({user_data.get('Cảnh giới')}) hãy tích cực tu luyện và điểm danh mỗi ngày."

        return "【Hệ Thống】\n\nKhông tìm thấy thông tin của ký chủ."
