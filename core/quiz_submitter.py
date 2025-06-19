# ehou_quiz_bot/core/quiz_submitter.py

from typing import Dict, Any
from config import settings

class QuizSubmitter:
    """Chuẩn bị payload và thực hiện submit đáp án."""
    def __init__(self, ehou_client):
        self.client = ehou_client

    def build_payload(self,
                      answers_map: Dict[str, str],
                      base_form_data: Dict[str, str],
                      finish_attempt: bool = False) -> Dict[str, Any]:
        """
        Xây dựng payload cuối cùng để submit.
        answers_map: ví dụ {'18101416:1': '0', '18101416:2': '3'}
        """
        payload = base_form_data.copy()

        # Thêm các câu trả lời
        for q_id_suffix, answer_index in answers_map.items():
            payload[f"q{q_id_suffix}_answer"] = str(answer_index)

        if finish_attempt:
            # Khi kết thúc, thường gửi 'finishattempt=1' và không có 'next'
            payload['finishattempt'] = '1'
            if 'next' in payload:
                del payload['next'] # Xóa nút "Next" nếu có
        else:
            # Khi chuyển trang, thường gửi 'next=1'
            payload['next'] = '1' # Hoặc giá trị của nút 'Tiếp theo'
            if 'finishattempt' in payload:
                 del payload['finishattempt']

        return {k: v for k, v in payload.items() if v is not None}

    def submit_page(self, payload: Dict[str, Any]) -> str | None:
        """Gửi payload của một trang và trả về HTML của trang tiếp theo hoặc trang kết quả."""
        print(f"[*] Submitter: Đang submit đáp án đến: {settings.EHOU_PROCESS_ATTEMPT_URL}")
        
        response = self.client.post_data(settings.EHOU_PROCESS_ATTEMPT_URL, data=payload)

        if response:
            print("[+] Submitter: Submit thành công!")
            # Kiểm tra xem có phải trang review không (dấu hiệu kết thúc)
            if "quizreviewsummary" in response.text or "/quiz/review.php" in response.url:
                print("[+] Submitter: Đã hoàn thành bài kiểm tra.")
                return None # Trả về None để báo hiệu kết thúc
            return response.text # Trả về HTML của trang tiếp theo
        else:
            print("[-] Submitter: Submit thất bại.")
            return "SUBMIT_ERROR"