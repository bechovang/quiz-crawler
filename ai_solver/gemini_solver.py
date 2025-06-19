# ehou_quiz_bot/ai_solver/gemini_solver.py

import google.generativeai as genai
from config import settings
from typing import List, Optional

class GeminiSolver:
    """Sử dụng Google Gemini API để giải câu hỏi trắc nghiệm."""
    def __init__(self):
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong config/settings.py")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=5,
            temperature=0.1, # Giảm tính ngẫu nhiên, tăng tính xác định
        )
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        try:
            self.model = genai.GenerativeModel(
                settings.GEMINI_MODEL_NAME,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            print(f"[+] AI Solver: Đã khởi tạo Gemini model '{settings.GEMINI_MODEL_NAME}' thành công.")
        except Exception as e:
            print(f"[-] AI Solver: Lỗi khi khởi tạo Gemini model: {e}")
            raise

    def get_answer_index(self, question_text: str, options: List[str]) -> Optional[int]:
        """Lấy index của đáp án từ Gemini (0 cho A, 1 cho B, ...)."""
        if not options:
            return None
            
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
            ai_answer_raw = response.text.strip().upper()
            
            # Trích xuất chữ cái hợp lệ đầu tiên
            for char_code in ai_answer_raw:
                if char_code in option_labels[:len(options)]:
                    print(f"[+] AI Solver: Gemini đề xuất: {char_code} (Raw: '{ai_answer_raw}')")
                    return option_labels.find(char_code)
            
            print(f"[-] AI Solver: Gemini trả về không hợp lệ: '{ai_answer_raw}'.")
            return None
        except Exception as e:
            print(f"[-] AI Solver: Lỗi khi gọi Gemini API: {e}")
            if 'response' in locals() and hasattr(response, 'prompt_feedback'):
                 print(f"[-] AI Solver: Gemini prompt feedback: {response.prompt_feedback}")
            return None