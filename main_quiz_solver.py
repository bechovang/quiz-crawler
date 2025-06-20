# ehou_quiz_bot/main.py (Sửa lỗi AttributeError)

import getpass
import time
from config import settings
from core.ehou_client import EhouClient
from core.quiz_parser import QuizParser
from core.quiz_submitter import QuizSubmitter
from ai_solver.gemini_solver import GeminiSolver

def main():
    print("--- BẮT ĐẦU KỊCH BẢN TỰ ĐỘNG GIẢI QUIZ EHOU ---")

    username = input("Nhập username EHOU: ")
    password = getpass.getpass("Nhập password EHOU: ")
    quiz_start_url = input("Nhập URL của trang làm bài quiz: ")

    try:
        ehou_client = EhouClient(username, password)
        ai_solver = GeminiSolver()
        # FIX: Khởi tạo lại QuizSubmitter vì chúng ta đã xóa build_payload khỏi nó trong phiên bản trước.
        # Bây giờ chúng ta sẽ thêm lại một phiên bản đơn giản hơn.
        quiz_submitter = QuizSubmitter(ehou_client)
    except Exception as e:
        print(f"\n[-] Lỗi khởi tạo: {e}")
        return

    if not ehou_client.login():
        return

    current_page_html = ehou_client.get_page_content(quiz_start_url)
    page_count = 0
    max_pages = 25
    summary_page_html = None

    # --- Vòng lặp xử lý các trang câu hỏi ---
    while current_page_html and current_page_html != "SUBMIT_ERROR" and page_count < max_pages:
        page_count += 1
        print(f"\n--- Đang xử lý trang Quiz thứ {page_count} ---")

        parser = QuizParser(current_page_html)
        questions = parser.extract_questions()
        
        if not questions:
            print("[*] Không tìm thấy câu hỏi nào. Giả định đã đến trang tóm tắt.")
            summary_page_html = current_page_html
            break

        # FIX: Gọi đúng tên phương thức đã đổi tên
        form_data = parser.extract_question_form_data()
        
        if not form_data:
            print("[-] Không thể parse form câu hỏi. Dừng lại.")
            break

        answers_for_page = {}
        for q in questions:
            print(f"[*] AI đang giải câu: {q['text'][:80]}...")
            time.sleep(settings.DELAY_BETWEEN_GEMINI_CALLS)
            answer_index = ai_solver.get_answer_index(q['text'], q['options'])
            if answer_index is not None:
                answers_for_page[q['id_suffix']] = str(answer_index)
                print(f"  [+] AI chọn: {q['options'][answer_index]} (index: {answer_index})")
            else:
                print("  [-] AI không đưa ra được đáp án, chọn mặc định đáp án đầu tiên.")
                answers_for_page[q['id_suffix']] = "0"

        payload = form_data.copy()
        for q_id_suffix, answer_index in answers_for_page.items():
            payload[f"q{q_id_suffix}_answer"] = str(answer_index)
        
        if not parser.has_next_page():
            payload.pop('next', None)
            print("[*] Submit trang câu hỏi cuối cùng để đến trang tóm tắt...")
        else:
            print("[*] Submit để chuyển sang trang câu hỏi tiếp theo...")

        current_page_html = quiz_submitter.submit_page(payload)
        time.sleep(settings.DELAY_AFTER_PAGE_SUBMIT)

    # --- BƯỚC NỘP BÀI CUỐI CÙNG TỪ TRANG TÓM TẮT ---
    if summary_page_html and summary_page_html != "SUBMIT_ERROR":
        print("\n--- Đang xử lý trang Tóm tắt và Nộp bài cuối cùng ---")
        
        summary_parser = QuizParser(summary_page_html)
        final_payload = summary_parser.extract_summary_form_data()
        
        if not final_payload:
            print("[-] Không thể parse form từ trang tóm tắt. Không thể nộp bài.")
        else:
            print("[*] Chuẩn bị gửi yêu cầu nộp bài cuối cùng...")
            time.sleep(settings.DELAY_AFTER_PAGE_SUBMIT)
            quiz_submitter.submit_page(final_payload)
            
    elif not summary_page_html:
        print("\n[-] Không thể đến được trang tóm tắt để nộp bài.")

    print("\n--- KỊCH BẢN KẾT THÚC ---")
    if page_count >= max_pages:
        print("[-] Đã đạt giới hạn số trang xử lý.")
    else:
        print("[+] Kịch bản đã hoàn thành.")

if __name__ == "__main__":
    main()