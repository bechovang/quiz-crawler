# ehou_quiz_bot/core/ehou_client.py (Phiên bản xử lý đăng nhập CAS - SSO)

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlencode, quote

class EhouClient:
    """
    Quản lý session và quy trình đăng nhập CAS (Single Sign-On) của EHOU.
    """
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })
        self.logged_in = False
        self.cas_base_url = 'https://cas.ehou.edu.vn/cas'
        self.moodle_base_url = 'https://learning.ehou.edu.vn'

    def login(self) -> bool:
        """
        Thực hiện quy trình đăng nhập CAS phức tạp.
        """
        if self.logged_in:
            return True

        print(f"[*] Bắt đầu quy trình đăng nhập CAS cho tài khoản: {self.username}...")

        try:
            # --- BƯỚC 1: Xác định URL đích và xây dựng URL đăng nhập CAS ---
            # 'service' là nơi CAS sẽ chuyển hướng về sau khi đăng nhập thành công
            service_url = f'{self.moodle_base_url}/login/index.php'
            cas_login_url = f'{self.cas_base_url}/login?service={quote(service_url)}'

            # --- BƯỚC 2: GET trang đăng nhập CAS để lấy form token (lt, execution) và cookie (JSESSIONID) ---
            print(f"[*] (1/4) Gửi yêu cầu GET đến: {self.cas_base_url}...")
            cas_page_res = self.session.get(cas_login_url, allow_redirects=True)
            cas_page_res.raise_for_status()

            soup = BeautifulSoup(cas_page_res.content, 'lxml')
            
            # Trích xuất các token cần thiết từ form
            lt_input = soup.find('input', {'name': 'lt'})
            execution_input = soup.find('input', {'name': 'execution'})

            if not (isinstance(lt_input, Tag) and isinstance(execution_input, Tag)):
                print("[-] Lỗi: Không thể tìm thấy các trường 'lt' hoặc 'execution' trong form đăng nhập CAS.")
                return False

            lt = lt_input['value']
            execution = execution_input['value']
            print("[+] Đã lấy được token 'lt' và 'execution'.")

            # --- BƯỚC 3: POST thông tin đăng nhập đến máy chủ CAS ---
            cas_post_payload = {
                'username': self.username,
                'password': self.password,
                'lt': lt,
                'execution': execution,
                '_eventId': 'submit',
                'submit': 'ĐĂNG NHẬP'
            }
            
            print("[*] (2/4) Gửi yêu cầu POST đến máy chủ CAS để xác thực...")
            # Không cho phép tự động chuyển hướng để chúng ta có thể bắt được "vé"
            cas_response = self.session.post(
                cas_login_url, 
                data=cas_post_payload, 
                allow_redirects=False # RẤT QUAN TRỌNG
            )

            # --- BƯỚC 4: Xử lý phản hồi từ CAS ---
            # Nếu thành công, CAS sẽ trả về status code 302 (Found/Redirect)
            # và header 'Location' sẽ chứa URL của Moodle với một "vé" (ticket).
            if cas_response.status_code != 302:
                print("[-] Đăng nhập CAS thất bại. Máy chủ không trả về mã chuyển hướng 302.")
                error_soup = BeautifulSoup(cas_response.content, 'lxml')
                error_div = error_soup.select_one('#msg.errors')
                if error_div:
                    print(f"[!] LÝ DO TỪ SERVER CAS: {error_div.get_text(strip=True)}")
                return False

            redirect_location_with_ticket = cas_response.headers.get('Location')
            if not redirect_location_with_ticket or 'ticket=' not in redirect_location_with_ticket:
                print("[-] Lỗi: Máy chủ CAS đã chuyển hướng nhưng không cung cấp 'ticket'.")
                return False
                
            print("[+] (3/4) Nhận được 'ticket' từ máy chủ CAS. Chuẩn bị xác thực với Moodle...")

            # --- BƯỚC 5: Truy cập Moodle với "vé" để tạo session Moodle ---
            # Bây giờ chúng ta cho phép requests đi theo các lần chuyển hướng tiếp theo
            print("[*] (4/4) Truy cập Moodle với 'ticket' để hoàn tất đăng nhập...")
            moodle_response = self.session.get(redirect_location_with_ticket, allow_redirects=True)
            moodle_response.raise_for_status()

            # Kiểm tra cuối cùng: đã đăng nhập thành công vào Moodle chưa?
            # Dấu hiệu là sự tồn tại của cookie 'MoodleSession' và trang có link logout
            if 'MoodleSession' in self.session.cookies and 'logout.php' in moodle_response.text:
                print("[+] Đăng nhập Moodle thành công thông qua CAS!")
                self.logged_in = True
                return True
            else:
                print("[-] Đăng nhập Moodle thất bại ở bước cuối cùng (xác thực ticket).")
                return False

        except requests.exceptions.RequestException as e:
            print(f"[-] Lỗi kết nối trong quá trình đăng nhập CAS: {e}")
            return False

    def get_page_content(self, url: str) -> str | None:
        if not self.logged_in:
            print("[-] Chưa đăng nhập. Vui lòng đăng nhập trước.")
            return None
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[-] Lỗi khi lấy nội dung trang {url}: {e}")
            return None

    def post_data(self, url: str, data: dict) -> requests.Response | None:
        if not self.logged_in:
            print("[-] Chưa đăng nhập. Vui lòng đăng nhập trước.")
            return None
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[-] Lỗi khi gửi POST đến {url}: {e}")
            return None