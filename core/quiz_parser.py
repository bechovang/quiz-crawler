# ehou_quiz_bot/core/quiz_parser.py (Đã sửa lỗi)

from bs4 import BeautifulSoup, Tag # <-- THÊM: Import 'Tag'
import re
from typing import List, Dict, Any

class QuizParser:
    """Phân tích HTML của trang quiz để trích xuất thông tin cần thiết."""
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    def extract_form_data(self) -> Dict[str, str]:
        """Trích xuất các input ẩn và thông tin quan trọng cho việc submit."""
        form_data = {}
        response_form = self.soup.find('form', id='responseform')

        # FIX: Kiểm tra response_form là một Tag trước khi tìm kiếm bên trong nó
        if not isinstance(response_form, Tag):
            print("[-] Parser: Không tìm thấy form#responseform. Việc submit sẽ thất bại.")
            return {}

        inputs = response_form.find_all('input', {'type': 'hidden'})
        for input_tag in inputs:
             # FIX: Đảm bảo input_tag là Tag trước khi gọi .get()
            if isinstance(input_tag, Tag):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value

        if 'sesskey' not in form_data or 'attempt' not in form_data:
            print("[-] Parser: Cảnh báo! Không tìm thấy sesskey hoặc attempt ID.")
        
        return form_data

    def extract_questions(self) -> List[Dict[str, Any]]:
        """Trích xuất danh sách câu hỏi và các lựa chọn."""
        questions = []
        question_divs = self.soup.select('div.que.multichoice')

        if not question_divs:
            print("[-] Parser: Không tìm thấy div câu hỏi nào với selector 'div.que.multichoice'.")
            return []

        print(f"[*] Parser: Tìm thấy {len(question_divs)} khối câu hỏi.")

        for q_div in question_divs:
            # Bỏ qua nếu q_div không phải là một Tag hợp lệ
            if not isinstance(q_div, Tag):
                continue
            
            q_data = {}
            radio_input = q_div.find('input', {'type': 'radio', 'name': re.compile(r'^q\d+:\d+_answer')})

            # FIX: Kiểm tra radio_input là một Tag trước khi sử dụng
            if isinstance(radio_input, Tag):
                name_attr = radio_input.get('name') 
                if isinstance(name_attr, str):
                    match = re.match(r'q(\d+:\d+)_answer', name_attr)
                    if match:
                        q_data['id_suffix'] = match.group(1)
                    else: continue
                else: continue
            else: continue
                
            qtext_el = q_div.select_one('.qtext')
            q_data['text'] = qtext_el.get_text(separator=' ', strip=True) if isinstance(qtext_el, Tag) else "Không tìm thấy nội dung câu hỏi."

            options = []
            option_labels = q_div.select('.answer div[class^="r"] label')
            for opt_label in option_labels:
                 if isinstance(opt_label, Tag):
                    options.append(opt_label.get_text(strip=True))

            q_data['options'] = options
            questions.append(q_data)

        return questions

    def is_final_page(self) -> bool:
        """Kiểm tra xem đây có phải là trang cuối cùng của bài thi không."""
        finish_button = self.soup.find('input', {'type': 'submit', 'name': 'finishattempt'})
        finish_link = self.soup.find('a', class_='endtestlink')
        return bool(finish_button or finish_link)