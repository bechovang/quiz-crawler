# ehou_quiz_bot/core/quiz_parser.py (Sửa lỗi NameError)

from bs4 import BeautifulSoup, Tag
import re
# FIX: Thêm import các kiểu dữ liệu từ module 'typing'
from typing import List, Dict, Any 

class QuizParser:
    """Phân tích HTML của trang quiz để trích xuất thông tin cần thiết."""
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    def extract_question_form_data(self) -> Dict[str, Any]:
        """Trích xuất dữ liệu từ form chứa câu hỏi (`responseform`)."""
        form_data = {}
        response_form = self.soup.find('form', id='responseform')
        if not isinstance(response_form, Tag):
            print("[-] Parser: Không tìm thấy form câu hỏi ('responseform').")
            return {}

        inputs = response_form.find_all('input')
        for input_tag in inputs:
            if isinstance(input_tag, Tag):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value
        return form_data

    def extract_summary_form_data(self) -> Dict[str, Any]:
        """Trích xuất dữ liệu từ form trên trang tóm tắt (summary.php)."""
        form_data = {}
        submit_button = self.soup.find('input', {'type': 'submit', 'value': re.compile(r'Nộp bài và kết thúc', re.I)})
        if not isinstance(submit_button, Tag):
            print("[-] Parser: Không tìm thấy nút 'Nộp bài và kết thúc' trên trang tóm tắt.")
            return {}
        
        summary_form = submit_button.find_parent('form')
        if not isinstance(summary_form, Tag):
            print("[-] Parser: Không tìm thấy form nộp bài trên trang tóm tắt.")
            return {}
        
        print("[*] Parser: Đã tìm thấy form trên trang tóm tắt.")
        inputs = summary_form.find_all('input', {'type': 'hidden'})
        for input_tag in inputs:
            if isinstance(input_tag, Tag):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value
        return form_data

    def extract_questions(self) -> List[Dict[str, Any]]:
        """Trích xuất danh sách câu hỏi và các lựa chọn từ trang làm bài."""
        questions = []
        question_divs = self.soup.select('div.que.multichoice')
        if not question_divs:
            return []
        
        for q_div in question_divs:
            if not isinstance(q_div, Tag):
                continue
            q_data = {}
            radio_input = q_div.find('input', {'type': 'radio', 'name': re.compile(r'^q\d+:\d+_answer')})
            if isinstance(radio_input, Tag):
                name_attr = radio_input.get('name') 
                if isinstance(name_attr, str):
                    match = re.match(r'q(\d+:\d+)_answer', name_attr)
                    if match:
                        q_data['id_suffix'] = match.group(1)
                    else:
                        continue
                else:
                    continue
            else:
                continue
            
            qtext_el = q_div.select_one('.qtext')
            q_data['text'] = qtext_el.get_text(separator=' ', strip=True) if isinstance(qtext_el, Tag) else "Lỗi parse text"
            
            options = []
            option_labels = q_div.select('.answer div[class^="r"] label')
            for opt_label in option_labels:
                 if isinstance(opt_label, Tag):
                    options.append(opt_label.get_text(strip=True))
            q_data['options'] = options
            questions.append(q_data)
        
        print(f"[*] Parser: Tìm thấy {len(questions)} khối câu hỏi.")
        return questions

    def extract_questions_with_answers(self) -> Dict[str, str]:
        """Trích xuất các cặp câu hỏi và đáp án ĐÚNG từ trang review.php."""
        qa_pairs = {}
        correct_questions = self.soup.select('div.que.correct')

        if not correct_questions:
            error_div = self.soup.select_one('.box.generalbox.error, .alert.alert-danger')
            if error_div:
                print(f"[-] Parser: Không thể truy cập trang review - {error_div.get_text(strip=True)}")
            return {}

        for q_div in correct_questions:
            if not isinstance(q_div, Tag):
                continue
            qtext_el = q_div.select_one('.qtext')
            correct_answer_el = q_div.select_one('.answer .correct label')

            if isinstance(qtext_el, Tag) and isinstance(correct_answer_el, Tag):
                question_text = ' '.join(qtext_el.get_text(strip=True).split())
                answer_text_raw = correct_answer_el.get_text(strip=True)
                answer_text = re.sub(r'^[a-z]\.\s*', '', answer_text_raw, flags=re.IGNORECASE).strip()
                
                if question_text and answer_text:
                    qa_pairs[question_text] = answer_text
        
        return qa_pairs
    
    def has_next_page(self) -> bool:
        """Kiểm tra xem có nút 'Trang kế tiếp' (Next page) trên trang hay không."""
        next_button = self.soup.select_one('input[type="submit"][name="next"]')
        return bool(next_button)