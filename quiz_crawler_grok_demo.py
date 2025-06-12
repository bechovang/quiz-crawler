import requests
from bs4 import BeautifulSoup
import pandas as pd
import getpass

# Thông tin đăng nhập
login_url = 'https://learning.ehou.edu.vn/login/index.php'
quiz_url = input('Nhập URL bài kiểm tra: ')  # Ví dụ: https://learning.ehou.edu.vn/mod/quiz/attempt.php?attempt=14216650&page=2
username = input('Nhập username: ')
password = getpass.getpass('Nhập password: ')

# Khởi tạo session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Bước 1: Đăng nhập
payload = {
    'username': username,
    'password': password,
    'rememberusername': 1
}
response = session.post(login_url, data=payload)

# Kiểm tra đăng nhập thành công
if 'logout.php' not in response.text:
    print('Đăng nhập thất bại. Vui lòng kiểm tra username/password.')
    exit()

# Bước 2: Truy cập bài kiểm tra
response = session.get(quiz_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Bước 3: Cào dữ liệu câu hỏi
questions = []
for q_div in soup.select('.que.multichoice'):
    question_text = q_div.select_one('.qtext').get_text(strip=True)
    options = [label.get_text(strip=True) for label in q_div.select('.answer label')]
    
    # Đảm bảo mỗi câu hỏi có đúng 4 đáp án
    while len(options) < 4:
        options.append('')
    
    questions.append({
        'Question': question_text,
        'Option A': options[0] if len(options) > 0 else '',
        'Option B': options[1] if len(options) > 1 else '',
        'Option C': options[2] if len(options) > 2 else '',
        'Option D': options[3] if len(options) > 3 else ''
    })

# Bước 4: Lưu thành file CSV
if questions:
    df = pd.DataFrame(questions)
    df.to_csv('quiz_questions.csv', index=False, encoding='utf-8')
    print('Đã lưu câu hỏi vào file quiz_questions.csv')
else:
    print('Không tìm thấy câu hỏi nào.')