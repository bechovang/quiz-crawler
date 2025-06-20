# ehou_quiz_bot/core/quiz_submitter.py (Đơn giản hóa)

from typing import Dict, Any
from config import settings

class QuizSubmitter:
    """Chuẩn bị payload và thực hiện submit đáp án."""
    def __init__(self, ehou_client):
        self.client = ehou_client

    # Phương thức này không cần thiết nữa, logic sẽ nằm trong main.py
    # def build_payload(...):

    def submit_page(self, payload: Dict[str, Any]) -> str | None:
        """Gửi payload và trả về HTML của trang tiếp theo hoặc None nếu kết thúc."""
        print(f"[*] Submitter: Đang submit đến: {settings.EHOU_PROCESS_ATTEMPT_URL}")
        # In ra một phần payload để debug
        print(f"[*] Submitter: Payload (một phần): {dict(list(payload.items())[:5])}...")
        
        response = self.client.post_data(settings.EHOU_PROCESS_ATTEMPT_URL, data=payload)

        if response:
            if "/quiz/review.php" in response.url:
                print("[+] Submitter: ĐÃ NỘP BÀI THÀNH CÔNG! Đang ở trang review.")
                return None # Trả về None để báo hiệu kết thúc
            print("[+] Submitter: Submit thành công, đang ở trang tiếp theo hoặc trang tóm tắt.")
            return response.text
        else:
            print("[-] Submitter: Submit thất bại.")
            return "SUBMIT_ERROR"