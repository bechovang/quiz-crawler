# ehou_quiz_bot/ai_solver/gemini_solver.py (Đã sửa lỗi pyright)

import google.generativeai as genai
import re
from config import settings
from typing import List, Optional
from database.question_bank import QuestionBank

class GeminiSolver:
    """Sử dụng Google Gemini API và ngân hàng câu hỏi để giải trắc nghiệm."""
    def __init__(self):
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong config/settings.py")
        
        # FIX: Thêm comment ignore để pyright bỏ qua cảnh báo không cần thiết
        genai.configure(api_key=settings.GEMINI_API_KEY)  # pyright: ignore[reportPrivateImportUsage]
        
        self.generation_config = genai.GenerationConfig(  # pyright: ignore[reportPrivateImportUsage]
            candidate_count=1,
            max_output_tokens=10,
            temperature=0.1,
        )
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        try:
            self.model = genai.GenerativeModel(  # pyright: ignore[reportPrivateImportUsage]
                settings.GEMINI_MODEL_NAME,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            print(f"[+] AI Solver: Đã khởi tạo Gemini model '{settings.GEMINI_MODEL_NAME}'.")
        except Exception as e:
            raise e

        self.question_bank = QuestionBank()
        count, _ = self.question_bank.get_stats()
        print(f"[+] AI Solver: Đã tải ngân hàng câu hỏi với {count} câu.")

    def get_answer_index(self, question_text: str, options: List[str]) -> Optional[int]:
        known_answer_text = self.question_bank.find_answer(question_text)
        if known_answer_text:
            print(f"  [+] BANK HIT: Tìm thấy đáp án trong ngân hàng: '{known_answer_text[:50]}...'")
            for i, option in enumerate(options):
                normalized_option = re.sub(r'^[a-z]\.\s*', '', option, flags=re.IGNORECASE).strip()
                if normalized_option == known_answer_text:
                    return i
            print("  [-] Cảnh báo: Tìm thấy text đáp án trong bank nhưng không khớp với lựa chọn nào.")

        print("  [*] AI CALL: Không có trong bank, đang gọi Gemini...")
        if not options: return None
        
        option_labels = "ABCDEFGHIJ"
        prompt_parts = [
            "Bạn là một trợ lý chuyên gia, nhiệm vụ của bạn là giải các câu hỏi trắc nghiệm một cách chính xác. "
            "Dựa vào câu hỏi và các lựa chọn dưới đây, hãy chọn ra một đáp án đúng nhất. "
            "CHỈ trả lời bằng MỘT CHỮ CÁI IN HOA duy nhất (ví dụ: A, B, C, hoặc D) tương ứng với lựa chọn đúng. "
            "Không thêm bất kỳ lời giải thích hay thông tin nào khác.\n"
            "---",
            f"Câu hỏi: {question_text}",
            "\nLựa chọn:"
        ]
        for i, option_text in enumerate(options):
            prompt_parts.append(f"{option_labels[i]}. {option_text}")
        prompt_parts.append("---\nĐáp án của bạn (chỉ một chữ cái):")
        
        prompt = "\n".join(prompt_parts)

        try:
            response = self.model.generate_content(prompt)
            ai_answer_raw = response.text.strip().upper() if response.text else ""
            for char_code in ai_answer_raw:
                if char_code in option_labels[:len(options)]:
                    return option_labels.find(char_code)
            return None
        except Exception as e:
            print(f"  [-] Lỗi khi gọi Gemini API: {e}")
            return None