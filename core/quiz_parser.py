# ehou_quiz_bot/core/quiz_parser.py

from bs4 import BeautifulSoup
import re
from typing import List, Dict, Tuple, Any

class QuizParser:
    """Phân tích HTML của trang quiz để trích xuất thông tin cần thiết."""
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    def extract_form_data(self) -> Dict[str, str]:
        """Trích xuất các input ẩn và thông tin quan trọng cho việc submit."""
        form_data = {}
        response_form = self.soup.find('form', id='responseform')
        if not response_form:
            print("[-] Parser: Không tìm thấy form#responseform. Việc submit sẽ thất bại.")
            return {}

        inputs = response_form.find_all('input', {'type': 'hidden'})
        for input_tag in inputs:
            name = input_tag.get('name')
            value = input_tag.get('value')
            if name:
                form_data[name] = value

        # Đảm bảo các trường quan trọng tồn tại
        if 'sesskey' not in form_data or 'attempt' not in form_data:
            print("[-] Parser: Cảnh báo! Không tìm thấy sesskey hoặc attempt ID.")
        
        return form_data

    def extract_questions(self) -> List[Dict[str, Any]]:
        """Trích xuất danh sách câu hỏi và các lựa chọn."""
        questions = []
        # Selector này cần được kiểm tra và điều chỉnh rất cẩn thận cho trang LÀM BÀI.
        question_divs = self.soup.select('div.que.multichoice')

        if not question_divs:
            print("[-] Parser: Không tìm thấy div câu hỏi nào với selector 'div.que.multichoice'.")
            return []

        print(f"[*] Parser: Tìm thấy {len(question_divs)} khối câu hỏi.")

        for q_div in question_divs:
            q_data = {}
            # Lấy ID và slot của câu hỏi từ name của input radio
            radio_input = q_div.find('input', {'type': 'radio', 'name': re.compile(r'^q\d+:\d+_answer')})
            if radio_input and radio_input.get('name'):
                name_attr = radio_input['name']
                match = re.match(r'q(\d+:\d+)_answer', name_attr)
                if match:
                    q_data['id_suffix'] = match.group(1)
                else:
                    continue # Bỏ qua nếu không parse được
            else:
                continue # Bỏ qua nếu không có radio input

            # Lấy nội dung câu hỏi
            qtext_el = q_div.select_one('.qtext')
            if qtext_el:
                q_data['text'] = qtext_el.get_text(separator=' ', strip=True)
            else:
                q_data['text'] = "Không tìm thấy nội dung câu hỏi."

            # Lấy các lựa chọn
            options = []
            option_labels = q_div.select('.answer div[class^="r"] label')
            for opt_label in option_labels:
                options.append(opt_label.get_text(strip=True))

            q_data['options'] = options
            questions.append(q_data)

        return questions

    def is_final_page(self) -> bool:
        """Kiểm tra xem đây có phải là trang cuối cùng của bài thi không."""
        # Dấu hiệu của trang cuối là có nút "Kết thúc bài làm..." hoặc "Nộp bài và kết thúc"
        finish_button = self.soup.find('input', {'type': 'submit', 'name': 'finishattempt'})
        finish_link = self.soup.find('a', class_='endtestlink')
        return bool(finish_button or finish_link)