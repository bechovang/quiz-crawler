# ehou_quiz_bot/config/settings.py

# --- EHOU URLs ---
# Cần được xác minh lại cho chính xác
EHOU_BASE_URL = 'https://learning.ehou.edu.vn'
EHOU_LOGIN_URL = f'{EHOU_BASE_URL}/login/index.php'
EHOU_PROCESS_ATTEMPT_URL = f'{EHOU_BASE_URL}/mod/quiz/processattempt.php'

# --- Gemini API Settings ---
# QUAN TRỌNG: Thay thế bằng API Key thực của bạn.
# Để an toàn, hãy xem xét việc load từ biến môi trường thay vì hardcode.
# Lấy API Key từ: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyBujJDc2KEdwQOyeZ9QNcAcKkWH3ubkR0E"

# Chọn model Gemini bạn muốn sử dụng
# 'gemini-1.5-flash-latest' - Nhanh, rẻ, phù hợp cho việc này
# 'gemini-pro' - Model cũ hơn nhưng ổn định
# 'gemini-1.5-pro-latest' - Mạnh mẽ hơn, chi phí cao hơn
GEMINI_MODEL_NAME = 'gemini-1.5-flash-latest'

# --- Automation Settings ---
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

 # Chờ sau khi nộp một trang câu hỏi để tải trang mới
# Độ trễ (giây) để tránh bị phát hiện hoặc bị block
DELAY_BETWEEN_GEMINI_CALLS = 1.5  # Thời gian chờ giữa các lần gọi API Gemini
DELAY_AFTER_PAGE_SUBMIT = 2.5     # Thời gian chờ sau khi nộp một trang câu hỏi
DELAY_BETWEEN_BANK_CRAWLS = 0.5   # Thời gian chờ giữa các lần cào ngân hàng câu hỏi
# FIX: Thêm biến còn thiếu vào đây
DELAY_BETWEEN_BANK_CRAWLSSUBMIT = 2.5     
# Thời gian chờ sau khi nộp một trang câu hỏi



