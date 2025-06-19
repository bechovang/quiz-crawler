# ehou_quiz_bot/main.py

import getpass
import time
from config import settings
from core.ehou_client import EhouClient
from core.quiz_parser import QuizParser
from core.quiz_submitter import QuizSubmitter
from ai_solver.gemini_solver import GeminiSolver

def main():
    """Hàm chính điều khiển toàn bộ kịch bản."""
    print("--- BẮT ĐẦU KỊCH BẢN TỰ ĐỘNG GIẢI QUIZ EHOU (Chế độ Kiểm thử) ---")

    # --- Nhập thông tin ---
    username = input("Nhập username EHOU: ")
    password = getpass.getpass("Nhập password EHOU: ")
    quiz_start_url = input("Nhập URL của trang làm bài quiz (trang bắt đầu hoặc trang resume): ")

    # --- Khởi tạo các client ---
    try:
        ehou_client = EhouClient(username, password)
        ai_solver = GeminiSolver()
        quiz_submitter = QuizSubmitter(ehou_client)
    except Exception as e:
        print(f"\n[-] Lỗi khởi tạo: {e}")
        return

    # --- Đăng nhập ---
    if not ehou_client.login():
        return

    # --- Vòng lặp xử lý các trang của bài quiz ---
    current_page_html = ehou_client.get_page_content(quiz_start_url)
    page_count = 0
    max_pages = 25 # Giới hạn an toàn

    while current_page_html and current_page_html != "SUBMIT_ERROR" and page_count < max_pages:
        page_count += 1
        print(f"\n--- Đang xử lý trang Quiz thứ {page_count} ---")

        parser = QuizParser(current_page_html)
        questions = parser.extract_questions()
        form_data = parser.extract_form_data()

        if not questions:
            print("[*] Không tìm thấy câu hỏi nào trên trang này. Có thể là trang cuối cùng.")
            # Nếu không có câu hỏi nhưng có form, có thể đây là trang xác nhận kết thúc
            if form_data:
                final_payload = quiz_submitter.build_payload({}, form_data, finish_attempt=True)
                quiz_submitter.submit_page(final_payload)
            break

        # --- Giải các câu hỏi bằng AI ---
        answers_for_page = {}
        for q in questions:
            print(f"[*] AI đang giải câu: {q['text'][:80]}...")
            
            # Chờ để tránh rate limit
            time.sleep(settings.DELAY_BETWEEN_GEMINI_CALLS)
            
            answer_index = ai_solver.get_answer_index(q['text'], q['options'])
            
            if answer_index is not None:
                answers_for_page[q['id_suffix']] = str(answer_index)
                print(f"  [+] AI chọn: {q['options'][answer_index]} (index: {answer_index})")
            else:
                print("  [-] AI không đưa ra được đáp án, chọn mặc định đáp án đầu tiên.")
                answers_for_page[q['id_suffix']] = "0" # Mặc định chọn A

        # --- Submit trang hiện tại ---
        is_last = parser.is_final_page()
        payload = quiz_submitter.build_payload(answers_for_page, form_data, finish_attempt=is_last)
        
        print(f"[*] Chuẩn bị submit trang {page_count}. Đây {'là' if is_last else 'không phải là'} trang cuối.")
        
        # Chờ trước khi submit
        time.sleep(settings.DELAY_AFTER_PAGE_SUBMIT)
        
        current_page_html = quiz_submitter.submit_page(payload)

    print("\n--- KỊCH BẢN KẾT THÚC ---")
    if page_count >= max_pages:
        print("[-] Đã đạt giới hạn số trang xử lý.")
    elif current_page_html == "SUBMIT_ERROR":
        print("[-] Dừng lại do lỗi submit.")
    else:
        print("[+] Kịch bản đã hoàn thành.")

if __name__ == "__main__":
    main()