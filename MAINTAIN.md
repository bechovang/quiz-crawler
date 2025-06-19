# Ghi chú Bảo trì và Phát triển

Tài liệu này dành cho các nhà phát triển muốn bảo trì hoặc mở rộng dự án `ehou_quiz_bot`.

## 1. Luồng hoạt động chính

1.  `main.py` khởi tạo các đối tượng: `EhouClient`, `GeminiSolver`, `QuizSubmitter`.
2.  `EhouClient` thực hiện đăng nhập và quản lý `requests.Session`.
3.  Vòng lặp chính trong `main.py` bắt đầu:
    a. Dùng `EhouClient` để lấy HTML của trang quiz hiện tại.
    b. `QuizParser` phân tích HTML để lấy:
        - Danh sách các câu hỏi (text, options, id_suffix).
        - Dữ liệu ẩn của form (sesskey, attempt, ...).
        - Kiểm tra xem có phải trang cuối không.
    c. Vòng lặp qua các câu hỏi:
        - `GeminiSolver` được gọi để lấy chỉ số (index) của đáp án.
        - Kết quả được lưu vào một dictionary `answers_for_page`.
    d. `QuizSubmitter` xây dựng payload cuối cùng từ `answers_for_page` và dữ liệu form.
    e. `EhouClient` (thông qua `QuizSubmitter`) gửi POST request chứa payload.
    f. HTML của trang tiếp theo được trả về và vòng lặp tiếp tục. Nếu không có trang tiếp theo, vòng lặp kết thúc.

## 2. Cách gỡ lỗi (Debugging)

### 2.1. Lỗi Đăng nhập
- Kiểm tra lại `username` và `password`.
- Trong `core/ehou_client.py`, bỏ comment các dòng `print(response.text)` để xem chi tiết lỗi từ server.
- Moodle có thể đã thêm cơ chế bảo vệ mới (ví dụ: CAPTCHA sau nhiều lần đăng nhập sai).

### 2.2. Lỗi Parser (Phổ biến nhất)
- Nếu chương trình báo "Không tìm thấy câu hỏi", hãy làm theo các bước sau:
    1.  Đăng nhập vào EHOU bằng trình duyệt.
    2.  Vào trang làm bài quiz.
    3.  Lưu lại toàn bộ mã nguồn HTML của trang (Ctrl+S).
    4.  Mở file `core/quiz_parser.py`.
    5.  Sử dụng file HTML đã lưu làm đầu vào để gỡ lỗi các selector của `BeautifulSoup` một cách độc lập.
    6.  Các selector cần kiểm tra: `div.que.multichoice`, `.qtext`, `.answer div[class^="r"] label`, `form#responseform`.
    7.  Đặc biệt chú ý cách lấy `id_suffix` từ `name` của thẻ input radio.

### 2.3. Lỗi Gemini API
- Đảm bảo API key là chính xác và đã được bật trong Google Cloud/AI Studio.
- Kiểm tra tài khoản thanh toán (billing) nếu bạn dùng model trả phí.
- Đọc kỹ thông báo lỗi từ API. Có thể là do `prompt` bị chặn bởi bộ lọc an toàn (safety filters). Các `safety_settings` trong `gemini_solver.py` đã được nới lỏng nhưng có thể không đủ.

### 2.4. Lỗi Submit
- Việc submit thất bại thường do `payload` bị thiếu hoặc sai một trường nào đó.
- Hãy in toàn bộ `payload` trong `core/quiz_submitter.py` trước khi gửi đi.
- So sánh nó với payload được gửi bởi trình duyệt thực (sử dụng tab Network trong Developer Tools) để tìm ra sự khác biệt. Các trường hay bị thiếu là `slots`, `thispage`, `nextpage`, hoặc một token ẩn nào đó.

## 3. Hướng phát triển thêm
- **Hỗ trợ nhiều loại câu hỏi hơn:**
    - Trả lời ngắn (Short Answer).
    - Nối cặp (Matching).
    - Điền vào chỗ trống (Fill in the blank).
    - Điều này đòi hỏi phải nâng cấp `QuizParser` và `GeminiSolver` (prompt engineering phức tạp hơn).
- **Tích hợp cơ chế retry:** Thêm logic thử lại cho các yêu cầu mạng hoặc các cuộc gọi API bị lỗi tạm thời.
- **Lưu trữ kết quả:** Ghi lại kết quả (điểm số, các câu trả lời đúng/sai) vào file log hoặc CSDL.
- **Giao diện người dùng:** Xây dựng một giao diện đơn giản (ví dụ: dùng `Streamlit` hoặc `Flask`) để dễ sử dụng hơn thay vì chạy trên terminal.
- **Cơ chế chống phát hiện nâng cao:**
    - Random hóa thời gian chờ (delay) trong một khoảng nhất định.
    - Mô phỏng chuyển động chuột và sự kiện gõ phím (sử dụng `selenium`).