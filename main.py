# ehou_quiz_bot/main.py

import getpass
import time
from config import settings
from core.ehou_client import EhouClient
from core.quiz_parser import QuizParser
from ai_solver.gemini_solver import GeminiSolver
from database.question_bank import QuestionBank

def run_quiz_solver(ehou_client: EhouClient):
    """Chạy kịch bản tự động giải quiz."""
    print("\n--- BẮT ĐẦU KỊCH BẢN TỰ ĐỘNG GIẢI QUIZ ---")
    quiz_start_url = input("Nhập URL của trang làm bài quiz (bắt đầu hoặc resume): ")

    try:
        ai_solver = GeminiSolver()
    except Exception as e:
        print(f"\n[-] Lỗi khởi tạo AI Solver: {e}")
        return

    current_page_html = ehou_client.get_page_content(quiz_start_url)
    page_count = 0
    max_pages = 25
    summary_page_html = None

    while current_page_html and current_page_html != "SUBMIT_ERROR" and page_count < max_pages:
        page_count += 1
        print(f"\n--- Đang xử lý trang Quiz thứ {page_count} ---")

        parser = QuizParser(current_page_html)
        questions = parser.extract_questions()
        
        if not questions:
            print("[*] Không tìm thấy câu hỏi nào. Giả định đã đến trang tóm tắt.")
            summary_page_html = current_page_html
            break

        form_data = parser.extract_question_form_data()
        if not form_data:
            print("[-] Không thể parse form câu hỏi. Dừng lại.")
            break

        answers_for_page = {}
        for q in questions:
            print(f"[*] Đang giải câu: {q['text'][:80]}...")
            time.sleep(settings.DELAY_BETWEEN_GEMINI_CALLS)
            answer_index = ai_solver.get_answer_index(q['text'], q['options'])
            if answer_index is not None:
                answers_for_page[q['id_suffix']] = str(answer_index)
            else:
                print("  [-] Không tìm được đáp án, chọn mặc định đáp án đầu tiên.")
                answers_for_page[q['id_suffix']] = "0"
        
        payload = form_data.copy()
        for q_id_suffix, answer_index in answers_for_page.items():
            payload[f"q{q_id_suffix}_answer"] = str(answer_index)
        
        if not parser.has_next_page():
            payload.pop('next', None)
            print("[*] Submit trang câu hỏi cuối cùng để đến trang tóm tắt...")
        else:
            print("[*] Submit để chuyển sang trang câu hỏi tiếp theo...")

        response = ehou_client.post_data(settings.EHOU_PROCESS_ATTEMPT_URL, payload)
        current_page_html = response.text if response else "SUBMIT_ERROR"
        time.sleep(settings.DELAY_AFTER_PAGE_SUBMIT)

    if summary_page_html and summary_page_html != "SUBMIT_ERROR":
        print("\n--- Đang xử lý trang Tóm tắt và Nộp bài cuối cùng ---")
        summary_parser = QuizParser(summary_page_html)
        final_payload = summary_parser.extract_summary_form_data()
        if not final_payload:
            print("[-] Không thể parse form từ trang tóm tắt.")
        else:
            print("[*] Chuẩn bị gửi yêu cầu nộp bài cuối cùng...")
            time.sleep(settings.DELAY_AFTER_PAGE_SUBMIT)
            response = ehou_client.post_data(settings.EHOU_PROCESS_ATTEMPT_URL, final_payload)
            if response and "/quiz/review.php" in response.url:
                 print("[+] ĐÃ NỘP BÀI THÀNH CÔNG!")
            
    elif not summary_page_html:
        print("\n[-] Không thể đến được trang tóm tắt để nộp bài.")

    print("\n--- KỊCH BẢN GIẢI BÀI TẬP KẾT THÚC ---")

def run_bank_builder(ehou_client: EhouClient):
    """Chạy kịch bản xây dựng ngân hàng câu hỏi."""
    print("\n--- BẮT ĐẦU KỊCH BẢN XÂY DỰNG NGÂN HÀNG CÂU HỎI ---")
    print("[!] Cảnh báo: Kịch bản này khai thác lỗ hổng IDOR. Chỉ sử dụng với sự cho phép.")
    
    try:
        start_id = int(input("Nhập 'attempt ID' bắt đầu để quét: "))
        count = int(input("Nhập số lượng 'attempt' muốn quét: "))
    except ValueError:
        print("[-] ID và số lượng phải là số nguyên.")
        return

    question_bank = QuestionBank()
    stats_count, stats_path = question_bank.get_stats()
    print(f"\n[*] Ngân hàng câu hỏi hiện tại: {stats_count} câu hỏi (tại '{stats_path}').")

    base_review_url = f"{settings.EHOU_BASE_URL}/mod/quiz/review.php?attempt="
    new_questions_found = 0

    for i in range(count):
        attempt_id = start_id + i
        target_url = f"{base_review_url}{attempt_id}"
        print(f"\n--- [{i+1}/{count}] Đang quét attempt ID: {attempt_id} ---")
        
        html_content = ehou_client.get_page_content(target_url)
        if not html_content:
            print("[-] Không nhận được nội dung. Bỏ qua.")
            time.sleep(1)
            continue

        parser = QuizParser(html_content)
        qa_pairs = parser.extract_questions_with_answers()
        if not qa_pairs:
            print("[*] Không có câu hỏi/đáp án nào được tìm thấy trên trang này.")
        else:
            for question, answer in qa_pairs.items():
                if question_bank.add_question(question, answer):
                    new_questions_found += 1
                    print(f"  [+] Đã thêm câu hỏi mới: {question[:50]}...")
        
        time.sleep(settings.DELAY_BETWEEN_BANK_CRAWLS)

    print("\n--- KẾT THÚC QUÁ TRÌNH QUÉT ---")
    final_count, _ = question_bank.get_stats()
    print(f"[+] Tìm thấy {new_questions_found} câu hỏi mới.")
    print(f"[+] Tổng số câu hỏi trong ngân hàng: {final_count}.")

def main_menu():
    """Hàm chính để hiển thị menu và điều hướng."""
    print("===== EHOU AUTOMATION SUITE =====")
    username = input("Nhập username EHOU: ")
    password = getpass.getpass("Nhập password EHOU: ")
    
    ehou_client = EhouClient(username, password)
    if not ehou_client.login():
        print("\n[-] Đăng nhập thất bại. Kết thúc chương trình.")
        return

    while True:
        print("\n" + "="*40)
        print("CHỌN CHỨC NĂNG BẠN MUỐN THỰC HIỆN:")
        print("  1. Tự động giải bài quiz")
        print("  2. Xây dựng ngân hàng câu hỏi (Cào đáp án)")
        print("  0. Thoát")
        print("="*40)
        
        choice = input("Lựa chọn của bạn (0, 1, 2): ")
        
        if choice == '1':
            run_quiz_solver(ehou_client)
            break
        elif choice == '2':
            run_bank_builder(ehou_client)
            break
        elif choice == '0':
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại.")

if __name__ == "__main__":
    main_menu()