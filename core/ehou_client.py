# ehou_quiz_bot/core/ehou_client.py (Đã sửa lỗi)

import requests
from bs4 import BeautifulSoup, Tag
from config import settings

class EhouClient:
    """Quản lý session và các tương tác HTTP cơ bản với EHOU."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': settings.DEFAULT_USER_AGENT})
        self.logged_in = False

    def login(self) -> bool:
        """Đăng nhập vào hệ thống EHOU và duy trì session."""
        if self.logged_in:
            return True

        print(f"[*] Đang đăng nhập vào EHOU với tài khoản: {self.username}...")
        login_payload = {
            'username': self.username,
            'password': self.password,
            'rememberusername': '1'
        }
        try:
            print("[*] Lấy login token từ trang đăng nhập...")
            login_page_res = self.session.get(settings.EHOU_LOGIN_URL)
            login_page_res.raise_for_status()
            soup = BeautifulSoup(login_page_res.content, 'lxml')
            
            logintoken_input = soup.find('input', {'name': 'logintoken'})
            
            if isinstance(logintoken_input, Tag):
                token_value = logintoken_input.get('value')
                # FIX: Kiểm tra token_value là một chuỗi (str) trước khi gán
                if token_value and isinstance(token_value, str):
                    login_payload['logintoken'] = token_value
                    print("[+] Đã tìm thấy login token.")
                else:
                    print("[-] Giá trị của login token không hợp lệ. Tiếp tục không có token.")
            else:
                print("[-] Không tìm thấy input cho login token. Vẫn tiếp tục thử đăng nhập...")

            response = self.session.post(settings.EHOU_LOGIN_URL, data=login_payload)
            response.raise_for_status()

            if 'logout.php' in response.text and "loginerrors" not in response.text:
                print("[+] Đăng nhập EHOU thành công!")
                self.logged_in = True
                return True
            else:
                print("[-] Đăng nhập EHOU thất bại. Vui lòng kiểm tra lại thông tin.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[-] Lỗi kết nối khi đăng nhập EHOU: {e}")
            return False

    def get_page_content(self, url: str) -> str | None:
        """Lấy nội dung HTML của một trang."""
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
        """Gửi POST request và trả về đối tượng response."""
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