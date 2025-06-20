cào đáp án, làm thêm hàng đợi , ai agent cluster

# EHOU Quiz Bot - White Hat Automation Test Suite

Đây là bộ công cụ được thiết kế cho mục đích **kiểm thử bảo mật (Hacker Mũ Trắng)** hệ thống `learning.ehou.edu.vn` (Moodle). Kịch bản chính là tự động hóa việc làm bài kiểm tra trắc nghiệm bằng cách sử dụng AI (Google Gemini) để gợi ý và điền đáp án.

**CẢNH BÁO QUAN TRỌNG:**
- **CHỈ SỬ DỤNG VỚI SỰ CHO PHÉP RÕ RÀNG VÀ BẰNG VĂN BẢN.**
- Việc sử dụng công cụ này để gian lận trong các kỳ thi thực tế là vi phạm nghiêm trọng quy chế học tập và có thể dẫn đến các hình thức kỷ luật cao nhất.
- Công cụ này được cung cấp cho mục đích nghiên cứu và kiểm thử an ninh hệ thống, giúp đánh giá các lỗ hổng trong quy trình kiểm tra trực tuyến. Nhà phát triển không chịu trách nhiệm cho bất kỳ hành vi lạm dụng nào.

## Tính năng

- Tự động đăng nhập vào hệ thống EHOU.
- Cào (parse) câu hỏi và các lựa chọn từ trang làm bài quiz.
- Tích hợp **Google Gemini API** để phân tích và chọn đáp án cho từng câu hỏi.
- Tự động xây dựng payload và submit bài làm (hỗ trợ các bài thi nhiều trang).
- Có cơ chế chờ (delay) để mô phỏng hành vi người dùng và tránh bị block.

## Cài đặt

### 1. Điều kiện tiên quyết
- Python 3.8+
- Tài khoản Google và API Key cho Gemini.

### 2. Lấy Google Gemini API Key
- Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey).
- Đăng nhập bằng tài khoản Google của bạn.
- Nhấn "Create API key" để tạo một API key mới. Sao chép key này.

### 3. Cấu hình dự án
- Clone repository này về máy.
- Mở file `config/settings.py`.
- Dán API key bạn vừa tạo vào biến `GEMINI_API_KEY`:
  ```python
  GEMINI_API_KEY = "AIz...your...actual...key..."
  ```

### 4. Cài đặt các thư viện
- Tạo và kích hoạt một môi trường ảo (khuyến khích):
  ```bash
  python -m venv venv
  # Trên Windows:
  # venv\Scripts\activate
  # Trên macOS/Linux:
  # source venv/bin/activate
  ```
- Cài đặt các thư viện cần thiết từ file `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## Sử dụng

1.  Mở terminal trong thư mục gốc của dự án (`ehou_quiz_bot/`).
2.  Chạy file `main.py`:
    ```bash
    python main.py
    ```
3.  Làm theo hướng dẫn trên màn hình:
    - Nhập `username` EHOU của bạn.
    - Nhập `password` EHOU (sẽ được ẩn khi gõ).
    - Dán `URL` của trang làm bài quiz. Đây phải là URL khi bạn đã vào trong bài làm, có thể là trang đầu tiên hoặc một trang bất kỳ nếu bạn muốn tiếp tục một lần làm dở.

Bot sẽ tự động chạy, giải quyết và nộp bài.

## Lưu ý quan trọng
- **HTML Parser (`core/quiz_parser.py`):** Đây là phần **nhạy cảm nhất** của dự án. Cấu trúc HTML của Moodle có thể thay đổi giữa các phiên bản hoặc các theme. Nếu bot không hoạt động, khả năng cao là do các selector CSS (`div.que.multichoice`, `.qtext`, ...) không còn đúng. Bạn cần sử dụng "Inspect Element" (F12) trên trình duyệt để kiểm tra và cập nhật lại các selector trong file này cho phù hợp.
- **Tính chính xác của AI:** AI có thể trả lời sai. Mục đích của kịch bản là kiểm thử khả năng tự động hóa, không phải để đạt điểm tuyệt đối.