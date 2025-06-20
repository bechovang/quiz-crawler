# ehou_quiz_bot/core/quiz_parser.py (Cập nhật parser trang tóm tắt)

from bs4 import BeautifulSoup, Tag
import re
from typing import List, Dict, Any

class QuizParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    def extract_question_form_data(self) -> Dict[str, str]:
        # ... (Giữ nguyên)
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
    
    # FIX: Cải thiện logic tìm form trên trang tóm tắt
    def extract_summary_form_data(self) -> Dict[str, Any]:
        """Trích xuất dữ liệu từ form trên trang tóm tắt (summary.php)."""
        form_data = {}
        
        # Tìm nút "Nộp bài và kết thúc" trước
        submit_button = self.soup.find('input', {'type': 'submit', 'value': re.compile(r'Nộp bài và kết thúc', re.I)})
        
        if not isinstance(submit_button, Tag):
            print("[-] Parser: Không tìm thấy nút 'Nộp bài và kết thúc' trên trang tóm tắt.")
            return {}
            
        # Tìm form cha của nút đó
        summary_form = submit_button.find_parent('form')
        
        if not isinstance(summary_form, Tag):
            print("[-] Parser: Không tìm thấy form nộp bài trên trang tóm tắt.")
            return {}
        
        print("[*] Parser: Đã tìm thấy form nộp bài trên trang tóm tắt.")
        
        # Lấy tất cả input ẩn trong form đó
        inputs = summary_form.find_all('input', {'type': 'hidden'})
        for input_tag in inputs:
            if isinstance(input_tag, Tag):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value
        
        # QUAN TRỌNG: Thêm cả nút submit vào payload, vì một số hệ thống có thể cần nó
        submit_name = submit_button.get('name')
        if submit_name: # Nút submit có thể có hoặc không có 'name'
            form_data[submit_name] = submit_button.get('value', 'Nộp bài và kết thúc')
        else: # Nếu không có name, ta có thể không cần gửi nó, nhưng cần cẩn thận
             print("[*] Parser: Nút submit không có thuộc tính 'name'.")


        return form_data

    def extract_questions(self) -> List[Dict[str, Any]]:
        # ... (Giữ nguyên)
        questions = []
        question_divs = self.soup.select('div.que.multichoice')
        if not question_divs: return []
        print(f"[*] Parser: Tìm thấy {len(question_divs)} khối câu hỏi.")
        for q_div in question_divs:
            if not isinstance(q_div, Tag): continue
            q_data = {}
            radio_input = q_div.find('input', {'type': 'radio', 'name': re.compile(r'^q\d+:\d+_answer')})
            if isinstance(radio_input, Tag):
                name_attr = radio_input.get('name')
                if isinstance(name_attr, str):
                    match = re.match(r'q(\d+:\d+)_answer', name_attr)
                    if match: q_data['id_suffix'] = match.group(1)
                    else: continue
                else: continue
            else: continue
            qtext_el = q_div.select_one('.qtext')
            q_data['text'] = qtext_el.get_text(separator=' ', strip=True) if isinstance(qtext_el, Tag) else "Lỗi parse text"
            options = []
            option_labels = q_div.select('.answer div[class^="r"] label')
            for opt_label in option_labels:
                 if isinstance(opt_label, Tag): options.append(opt_label.get_text(strip=True))
            q_data['options'] = options
            questions.append(q_data)
        return questions

    def has_next_page(self) -> bool:
        # ... (Giữ nguyên)
        next_button = self.soup.select_one('input[type="submit"][name="next"]')
        return bool(next_button)