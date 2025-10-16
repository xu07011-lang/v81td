import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from collections import deque, defaultdict, Counter
import random
import hashlib
import platform
import subprocess
import string
import urllib.parse

# Check và cài đặt các thư viện cần thiết
try:
    from colorama import init
    init(autoreset=True) # Vẫn giữ colorama init cho phần xác thực key
    import pytz
    from faker import Faker
    from requests import session
    # Thư viện Rich cho giao diện
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
except ImportError:
    print('__Đang cài đặt thư viện nâng cấp, vui lòng chờ...__')
    os.system("pip install requests colorama pytz faker pystyle bs4 rich")
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# =====================================================================================
# PHẦN 1: MÃ NGUỒN TỪ KEYV8.PY (LOGIC XÁC THỰC - GIỮ NGUYÊN)
# =====================================================================================

# CONFIGURATION FOR VIP KEY
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display (từ keyv8.py)
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Đổi tên hàm banner của file banner.py để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Tool VIP V8
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# DEVICE ID AND IP ADDRESS FUNCTIONS
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]

    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")


# FREE KEY HANDLING FUNCTIONS
def luu_thong_tin_ip(ip, key, expiration_date):
    """Saves free key information to a json file."""
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    """Loads free key information from the json file."""
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
    """Checks for a saved free key for the current IP."""
    data = tai_thong_tin_ip()
    if data and ip in data:
        try:
            expiration_date = datetime.fromisoformat(data[ip]['expiration_date'])
            if expiration_date > datetime.now():
                return data[ip]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_key_and_url(ip_address):
    """Creates a free key and a URL to bypass the link."""
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'TDK{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://buffttfbinta.blogspot.com/2025/10/t.html?m={key}' # Link này có thể giữ nguyên hoặc thay đổi tùy admin
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    """Handles the entire process of obtaining a free key."""
    url, key, expiration_date = generate_key_and_url(ip_address)

    with ThreadPoolExecutor(max_workers=1) as executor:
        yeumoney_future = executor.submit(get_shortened_link_phu, url)
        yeumoney_data = yeumoney_future.result()

    if yeumoney_data and yeumoney_data.get('status') == "error":
        print(yeumoney_data.get('message'))
        return False

    link_key_yeumoney = yeumoney_data.get('shortenedUrl')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_yeumoney}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            sleep(2)
            luu_thong_tin_ip(ip_address, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_yeumoney}{trang}')


# VIP KEY HANDLING FUNCTIONS
def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()

        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """Checks the VIP key from the URL on GitHub."""
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts

                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# MAIN AUTHENTICATION FLOW
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)
    key_info = {}

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False, None, None

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                key_info = {'type': 'VIP', 'key': cached_vip_info['key'], 'expiry': cached_vip_info['expiration_date']}
                sleep(3)
                return True, device_id, key_info
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    if kiem_tra_ip(ip_address):
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn. Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
        time.sleep(2)
        return True, device_id, key_info

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Dùng trong ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)

                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    key_info = {'type': 'VIP', 'key': vip_key_input, 'expiry': expiry_date_str}
                    sleep(3)
                    return True, device_id, key_info
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                if process_free_key(ip_address):
                    key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
                    return True, device_id, key_info
                else:
                    return False, None, None

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except (KeyboardInterrupt):
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()


# =====================================================================================
# PHẦN 2: MÃ NGUỒN TOOL CHÍNH (NÂNG CẤP V8)
# =====================================================================================

console = Console()

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}
ALL_NV_IDS = list(NV.keys())

# Lớp quản lý trạng thái chung (dùng cho việc tránh cược trùng)
class SharedStateManager:
    def __init__(self, api_endpoint, user_id):
        self.api_endpoint = api_endpoint
        self.user_id = user_id
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_shared_bets(self, issue_id):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get(str(issue_id), {})
            return {}
        except (requests.RequestException, json.JSONDecodeError):
            return {}

    def claim_bet(self, issue_id, bet_on_char):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            data = {}
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict): data = {}
                except json.JSONDecodeError: data = {}
            
            current_issue_num = int(issue_id)
            keys_to_delete = [key for key in data.keys() if not key.isdigit() or int(key) < current_issue_num - 5]
            for key in keys_to_delete:
                del data[key]

            issue_key = str(issue_id)
            if issue_key not in data: data[issue_key] = {}
            
            data[issue_key][str(bet_on_char)] = self.user_id
            requests.put(f"{self.api_endpoint}", data=json.dumps(data), headers=self.headers, timeout=5)
            return True
        except Exception:
            return False

# NÂNG CẤP V8: Hệ thống 50 Logics
class LogicEngineV9:
    def __init__(self, state_manager, history_min_size=10):
        self.history = deque(maxlen=200)
        self.state_manager = state_manager
        self.history_min_size = history_min_size
        self.logics = self._get_all_logics()

    def add_result(self, winner_id):
        if winner_id in NV:
            self.history.append(winner_id)

    def _get_all_logics(self):
        # Tạo danh sách 50 hàm logic
        return [getattr(self, f"logic_{i:02}") for i in range(1, 51)]
    
    # === BỘ 50 LOGICS ===
    def logic_01(self): return Counter(self.history).most_common()[-1][0] if self.history else random.choice(ALL_NV_IDS)
    def logic_02(self): return Counter(self.history).most_common(1)[0][0] if self.history else random.choice(ALL_NV_IDS)
    def logic_03(self): return self.history[-1] if self.history else random.choice(ALL_NV_IDS)
    def logic_04(self): return self.history[-2] if len(self.history) > 1 else self.logic_01()
    def logic_05(self):
        seen = set(self.history)
        unseen = [c for c in ALL_NV_IDS if c not in seen]
        return random.choice(unseen) if unseen else self.logic_01()
    def logic_06(self):
        freq = Counter(list(self.history)[-10:])
        return freq.most_common()[-1][0] if freq else self.logic_01()
    def logic_07(self):
        freq = Counter(list(self.history)[-10:])
        return freq.most_common(1)[0][0] if freq else self.logic_02()
    def logic_08(self):
        if len(self.history) < 2: return self.logic_01()
        transitions = defaultdict(int)
        for i in range(len(self.history) - 1):
            if self.history[i] == self.history[-1]:
                transitions[self.history[i+1]] += 1
        return max(transitions, key=transitions.get) if transitions else self.logic_03()
    def logic_09(self): return (self.history[-1] % 6) + 1 if self.history else 1
    def logic_10(self): return 7 - self.history[-1] if self.history else 6
    def logic_11(self): return random.choice([c for c in ALL_NV_IDS if c != self.history[-1]]) if self.history else random.choice(ALL_NV_IDS)
    def logic_12(self): return list(self.history)[-5] if len(self.history) >= 5 else self.logic_04()
    def logic_13(self):
        evens = [c for c in self.history if c % 2 == 0]
        return Counter(evens).most_common(1)[0][0] if evens else 2
    def logic_14(self):
        odds = [c for c in self.history if c % 2 != 0]
        return Counter(odds).most_common(1)[0][0] if odds else 1
    def logic_15(self): return (self.logic_01() + self.logic_02()) % 6 + 1
    def logic_16(self):
        if len(self.history) < 3: return self.logic_01()
        return self.history[-1] if self.history[-1] == self.history[-3] else self.logic_01()
    def logic_17(self): return 1 if len(self.history) % 2 == 0 else 6
    def logic_18(self): return 3 if len(self.history) % 2 == 0 else 4
    def logic_19(self):
        if not self.history: return 1
        return max(set(self.history), key=list(self.history).count)
    def logic_20(self):
        if not self.history: return 1
        return min(set(self.history), key=list(self.history).count)
    def logic_21(self):
        pairs = Counter(zip(self.history, self.history[1:]))
        if not pairs: return self.logic_01()
        last = self.history[-1]
        next_cand = [p[1] for p in pairs if p[0] == last]
        return Counter(next_cand).most_common(1)[0][0] if next_cand else self.logic_01()
    def logic_22(self):
        if len(self.history) < 2: return self.logic_01()
        return abs(self.history[-1] - self.history[-2]) or 1
    def logic_23(self): return (sum(self.history) % 6) + 1 if self.history else 1
    def logic_24(self):
        recent = list(self.history)[-5:]
        return Counter(recent).most_common(1)[0][0] if recent else self.logic_02()
    def logic_25(self): return (self.history[0] if self.history else 1)
    def logic_26(self): return (self.history[-1] + 2) % 6 + 1 if self.history else 3
    def logic_27(self): return (self.history[-1] - 2) % 6 + 1 if self.history else 5
    def logic_28(self):
        runs = [len(list(g)) for k, g in itertools.groupby(self.history)] if self.history else []
        return runs[-1] if runs and runs[-1] <= 6 else self.logic_01()
    def logic_29(self):
        import itertools
        return self.logic_28() # Cần thư viện itertools
    def logic_30(self): return sum(self.history[-3:]) % 6 + 1 if len(self.history) >= 3 else self.logic_01()
    def logic_31(self): return (self.history[-1] * 2) % 6 + 1 if self.history else 2
    def logic_32(self):
        if len(self.history) < 4: return self.logic_01()
        return self.history[-4]
    def logic_33(self):
        if not self.history: return 1
        return round(sum(self.history) / len(self.history)) % 6 + 1
    def logic_34(self):
        last_seen = {val: i for i, val in enumerate(self.history)}
        return min(last_seen, key=last_seen.get) if last_seen else 1
    def logic_35(self):
        last_seen = {val: i for i, val in enumerate(self.history)}
        return max(last_seen, key=last_seen.get) if last_seen else 6
    def logic_36(self): return (self.logic_13() + self.logic_14()) % 6 + 1
    def logic_37(self):
        s = set(self.history)
        return (list(s)[0] if s else 1)
    def logic_38(self):
        if len(self.history) < 2: return self.logic_01()
        if self.history[-1] > self.history[-2]: return max(ALL_NV_IDS)
        else: return min(ALL_NV_IDS)
    def logic_39(self): return 6 if self.history and self.history[-1] == 1 else 1
    def logic_40(self): return 3 if self.history and self.history[-1] in [1, 2] else 5
    def logic_41(self):
        if len(self.history) < 2: return 1
        return self.history[-1] if self.history[-1] == self.history[-2] else self.logic_01()
    def logic_42(self): return len(set(self.history)) if self.history else 1
    def logic_43(self): return (self.history[-1] + self.history[0]) % 6 + 1 if len(self.history) > 1 else 1
    def logic_44(self): return 2 if self.history and self.history[-1] % 2 == 1 else 1
    def logic_45(self):
        counts = Counter(self.history)
        return min([c for c in ALL_NV_IDS if counts[c] == 1], default=self.logic_01())
    def logic_46(self):
        if len(self.history) < 10: return self.logic_01()
        first_half = Counter(list(self.history)[-10:-5])
        second_half = Counter(list(self.history)[-5:])
        return (second_half.most_common(1)[0][0] if second_half else 1) if not first_half or second_half.most_common(1)[0][1] > first_half.most_common(1)[0][1] else (first_half.most_common(1)[0][0] if first_half else 1)
    def logic_47(self): return self.logic_01()
    def logic_48(self): return self.logic_02()
    def logic_49(self): return self.logic_03()
    def logic_50(self): return random.choice(ALL_NV_IDS)

    # =================== PHẦN ĐƯỢC THAY ĐỔI THEO YÊU CẦU ===================
    def analyze_and_select(self, issue_id):
        # ----- Phần 1: Chọn ứng viên ban đầu và xác định top 6 -----
        if len(self.history) < self.history_min_size:
            candidate = random.choice(ALL_NV_IDS)
            top6_char = -1 # Giá trị mặc định không ảnh hưởng
        else:
            # Chọn logic từ bộ 50
            selected_logic = self.logics[issue_id % len(self.logics)]
            candidate = selected_logic()

            # Logic mới: Phân tích tần suất và xác định nhân vật về ít nhất (top 6)
            frequencies = Counter(self.history)
            full_frequencies = {char_id: frequencies.get(char_id, 0) for char_id in ALL_NV_IDS}
            top6_char = min(full_frequencies, key=full_frequencies.get)
            
            # Nếu ứng viên ban đầu là top 6, bot không được phép cược và phải chọn lại
            if candidate == top6_char:
                alternative_choices = [c for c in ALL_NV_IDS if c != top6_char]
                if alternative_choices:
                    candidate = random.choice(alternative_choices)
    
        # ----- Phần 2: Chống cược trùng, có xem xét đến top 6 -----
        shared_bets = self.state_manager.get_shared_bets(issue_id)
        claimed_chars = [int(k) for k in shared_bets.keys()]

        # Kiểm tra xem ứng viên cuối cùng của chúng ta (đã né top 6) có bị người khác cược trùng không
        if candidate not in claimed_chars:
            # Nếu không trùng, tiến hành đặt cược
            self.state_manager.claim_bet(issue_id, candidate)
            return candidate
        else:
            # Nếu bị trùng, phải tìm phương án thay thế
            
            # Lấy danh sách tất cả các Nhân vật chưa bị ai cược
            available_options = [c for c in ALL_NV_IDS if c not in claimed_chars]

            if not available_options:
                # Cực hiếm: Toàn bộ 6 NV đã bị cược, không còn lựa chọn nào.
                # Trả về một NV ngẫu nhiên và để API game tự xử lý.
                return random.choice(ALL_NV_IDS)

            # Trong số các NV chưa bị cược, ưu tiên chọn những NV không phải top 6
            preferred_options = [opt for opt in available_options if opt != top6_char]

            final_choice = None
            if preferred_options:
                # Nếu có lựa chọn vừa khả dụng vừa không phải top 6 -> Chọn lựa chọn này
                final_choice = random.choice(preferred_options)
            else:
                # Nếu không còn lựa chọn nào khác ngoài top 6 (ví dụ 5 người dùng khác đã cược hết 5 NV kia)
                # -> Bất đắc dĩ phải chọn NV còn lại duy nhất, chính là top 6.
                final_choice = random.choice(available_options)
                
            self.state_manager.claim_bet(issue_id, final_choice)
            return final_choice
    # =================== KẾT THÚC PHẦN THAY ĐỔI ===================


# =====================================================================================
# PHẦN GIAO DIỆN VÀ HIỂN THỊ (SỬA LỖI)
# =====================================================================================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def format_time(seconds):
    if seconds < 0: return "0 ngày 0 giờ 0 phút"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} ngày {hours} giờ {minutes} phút"

def add_log(logs_deque, message):
    hanoi_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(hanoi_tz).strftime('%H:%M:%S')
    logs_deque.append(f"[grey70]{timestamp}[/grey70] {message}")

def generate_dashboard(config, stats, wallet_asset, logs, coin_type, status_message, key_info) -> Panel:
    total_games = stats['win'] + stats['lose']
    win_rate = (stats['win'] / total_games * 100) if total_games > 0 else 0
    profit = wallet_asset.get(coin_type, 0) - stats['asset_0']
    profit_str = f"[bold green]+{profit:,.4f}[/bold green]" if profit >= 0 else f"[bold red]{profit:,.4f}[/bold red]"

    stats_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    stats_table.add_column(style="cyan"); stats_table.add_column(style="white")
    stats_table.add_row("Phiên Bản", "LOGIC V8")
    stats_table.add_row("Lợi Nhuận", f"{profit_str} {coin_type}")
    stats_table.add_row("Tổng Trận", str(total_games))
    stats_table.add_row("Thắng / Thua", f"[green]{stats['win']}[/green] / [red]{stats['lose']}[/red] ({win_rate:.2f}%)")
    stats_table.add_row("Chuỗi Thắng", f"[green]{stats['streak']}[/green] (Max: {stats['max_streak']})")
    stats_table.add_row("Chuỗi Thua", f"[red]{stats['lose_streak']}[/red]")
    # NÂNG CẤP V9: Thêm dòng thống kê thua liên tiếp
    lt_stats = stats['consecutive_loss_counts']
    stats_table.add_row("Tổng Thua L.Tiếp (1/2/3/4)", f"{lt_stats[1]} / {lt_stats[2]} / {lt_stats[3]} / {lt_stats[4]}")

    config_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    config_table.add_column(style="cyan"); config_table.add_column(style="yellow")
    config_table.add_row("Cược Cơ Bản", f"{config['bet_amount0']} {coin_type}")
    config_table.add_row("Hệ Số Gấp", str(config['heso']))
    config_table.add_row("Chế Độ Nghỉ", f"Chơi {config['delay1']} nghỉ {config['delay2']}")
    
    balance_table = Table(title="Số Dư", show_header=True, header_style="bold magenta", box=None)
    balance_table.add_column("Loại Tiền", style="cyan", justify="left")
    balance_table.add_column("Số Lượng", style="white", justify="right")
    balance_table.add_row("BUILD", f"{wallet_asset.get('BUILD', 0.0):,.4f}")
    balance_table.add_row("WORLD", f"{wallet_asset.get('WORLD', 0.0):,.4f}")
    balance_table.add_row("USDT", f"{wallet_asset.get('USDT', 0.0):,.4f}")
    
    # *** BẮT ĐẦU THAY ĐỔI: TẠO BẢNG THÔNG TIN KEY ***
    key_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    key_table.add_column(style="cyan"); key_table.add_column(style="white")
    
    if key_info.get('type') == 'VIP':
        key_table.add_row("Loại Key", "[bold gold1]VIP[/bold gold1]")
        key_table.add_row("Key", f"[gold1]{key_info.get('key', 'N/A')}[/gold1]")
        key_table.add_row("Hạn Dùng", f"[yellow]{key_info.get('expiry', 'N/A')}[/yellow]")
    elif key_info.get('type') == 'Free':
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(hcm_tz)
        midnight = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        delta = midnight - now
        
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        key_table.add_row("Loại Key", "[bold green]Free[/bold green]")
        key_table.add_row("Hết hạn vào", "[green]00:00:00 hàng ngày[/green]")
        key_table.add_row("Thời gian còn", f"[yellow]{countdown}[/yellow]")
    
    key_panel = Panel(key_table, title="[bold]Thông Tin Key[/bold]", border_style="blue")
    # *** KẾT THÚC THAY ĐỔI ***

    info_layout = Table.grid(expand=True)
    info_layout.add_column(ratio=1); info_layout.add_column(ratio=1)
    info_layout.add_row(Panel(stats_table, title="[bold]Thống Kê[/bold]", border_style="blue"), Panel(config_table, title="[bold]Cấu Hình[/bold]", border_style="blue"))
    # *** THAY ĐỔI: THÊM KEY PANEL VÀO GIAO DIỆN ***
    info_layout.add_row(Panel(balance_table, border_style="blue"), key_panel)

    # ########################################################################## #
    # ## THAY ĐỔI THEO YÊU CẦU: Thêm `reversed()` để đảo ngược thứ tự nhật ký ## #
    # ########################################################################## #
    log_panel = Panel("\n".join(reversed(logs)), title="[bold]Nhật Ký Hoạt Động[/bold]", border_style="green", height=12)
    
    status_panel = Panel(Align.center(Text(status_message, justify="center")), title="[bold]Trạng Thái[/bold]", border_style="yellow", height=3)
    
    main_grid = Table.grid(expand=True)
    main_grid.add_row(status_panel)
    main_grid.add_row(info_layout)
    main_grid.add_row(log_panel)
    
    dashboard = Panel(
        main_grid,
        title=f"[bold gold1]TOOL VIP V8[/bold gold1] - Thời gian chạy: {format_time(time.time() - config['start_time'])}",
        border_style="bold magenta"
    )
    return dashboard

# =====================================================================================
# CÁC HÀM LOGIC VÀ API
# =====================================================================================
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        console.print(f"[cyan]Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): [/cyan]", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(f"\n[yellow]Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây[/yellow]")
    console.print(f"[cyan]📋 Vui lòng nhập link của bạn: [/cyan]", end=''); link = input()
    user_id = re.search(r'userId=(\d+)', link).group(1)
    secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    console.print(f"[green]    ✓ Lấy thông tin thành công! User ID: {user_id}[/green]")
    json_data = {'user-id': user_id, 'user-secret-key': secret_key}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def populate_initial_history(s, headers, logic_engine):
    console.print(f"\n[green]Đang lấy dữ liệu lịch sử ban đầu...[/green]")
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            for issue_data in reversed(response['data']['recent_10']):
                logic_engine.add_result(issue_data['result'][0])
            console.print(f"[green]✓ Nạp thành công lịch sử {len(response['data']['recent_10'])} ván.[/green]"); return True
    except Exception as e: console.print(f"[red]Lỗi khi nạp lịch sử: {e}[/red]")
    return False

def fetch_latest_issue_info(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            latest_issue = response['data']['recent_10'][0]; return latest_issue['issue_id'], latest_issue
    except Exception: return None, None
    return None, None

def check_issue_result(s, headers, kq, ki):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        for issue in response['data']['recent_10']:
            if int(issue['issue_id']) == int(ki):
                actual_winner = issue['result'][0]; return actual_winner != kq, actual_winner
    except Exception: return None, None
    return None, None

def user_asset(s, headers):
    try:
        json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
        return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
    except Exception as e:
        console.print(f"[red]Lỗi khi lấy số dư: {e}. Thử lại...[/red]"); time.sleep(2); return user_asset(s, headers)

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount, logs):
    try:
        bet_amount_randomized = round(bet_amount * random.uniform(0.995, 1.005), 8)
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': bet_amount_randomized}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        
        # Không log lỗi ở đây nữa, sẽ xử lý ở vòng lặp chính để tránh log trùng lặp
        return response
    except requests.exceptions.RequestException as e:
        add_log(logs, f"[red]Lỗi mạng khi đặt cược:[/red] [white]{e}[/white]")
        return None

def get_user_input(prompt, input_type=float):
    while True:
        try:
            console.print(prompt, end="")
            value = input_type(input())
            return value
        except ValueError:
            console.print("[bold red]Định dạng không hợp lệ, vui lòng nhập lại một số.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Đã xảy ra lỗi: {e}. Vui lòng thử lại.[/bold red]")

# Vòng lặp chính của tool
def main_cdtd(device_id, key_info):
    s = requests.Session()
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], 'user-agent': 'Mozilla/5.0'}

    clear_screen()
    
    asset = user_asset(s, headers)
    console.print(f"[cyan]Chọn loại tiền bạn muốn chơi:[/cyan]\n  1. USDT\n  2. BUILD\n  3. WORLD")
    while True:
        console.print(f'[cyan]Nhập lựa chọn (1/2/3): [/cyan]', end="")
        x = input()
        if x in ['1', '2', '3']: Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]; break
        else: console.print(f"[red]Lựa chọn không hợp lệ, vui lòng nhập lại...[/red]")

    bet_amount0 = get_user_input(f'[cyan]Nhập số {Coin} muốn đặt ban đầu: [/cyan]', float)
    heso = get_user_input(f'[cyan]Nhập hệ số cược sau khi thua: [/cyan]', int)
    delay1 = get_user_input(f'[cyan]Chơi bao nhiêu ván thì nghỉ (999 nếu không nghỉ): [/cyan]', int)
    delay2 = get_user_input(f'[cyan]Nghỉ trong bao nhiêu ván: [/cyan]', int)
    
    # NÂNG CẤP V9: Tự động bật chống cược trùng
    SHARED_API_ENDPOINT = "https://api.jsonblob.com/api/jsonBlob/1286918519102373888"
    user_unique_id = hashlib.sha256(device_id.encode()).hexdigest()[:8]
    state_manager = SharedStateManager(SHARED_API_ENDPOINT, user_unique_id)
    logic_engine = LogicEngineV9(state_manager)

    # NÂNG CẤP V9: Thêm bộ đếm thua liên tiếp
    stats = {
        'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 
        'asset_0': asset.get(Coin, 0), 'consecutive_loss_counts': defaultdict(int)
    }
    config = {'bet_amount0': bet_amount0, 'heso': heso, 'delay1': delay1, 'delay2': delay2, 'start_time': time.time()}
    logs = deque(maxlen=10); tong_van = 0
    
    # Thêm bộ nhớ để chống cược lặp lại một ván
    attempted_bets = deque(maxlen=100)

    populate_initial_history(s, headers, logic_engine); time.sleep(2)
    last_known_id, _ = fetch_latest_issue_info(s, headers)
    if not last_known_id:
        console.print(f"[red]Không thể lấy ID ván đầu tiên. Vui lòng kiểm tra lại mạng và API.[/red]")
        sys.exit()

    with Live(generate_dashboard(config, stats, asset, logs, Coin, "", key_info), console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                current_asset = user_asset(s, headers)
                status_msg = f"Đang chờ ván #{last_known_id + 1} bắt đầu..."
                live.update(generate_dashboard(config, stats, current_asset, logs, Coin, status_msg, key_info), refresh=True)

                newly_completed_id = last_known_id
                while newly_completed_id == last_known_id:
                    time.sleep(1)
                    newly_completed_id, newly_completed_issue_data = fetch_latest_issue_info(s, headers)
                    if newly_completed_id is None: newly_completed_id = last_known_id

                last_known_id = newly_completed_id
                if newly_completed_issue_data and 'result' in newly_completed_issue_data:
                    logic_engine.add_result(newly_completed_issue_data['result'][0])

                tong_van += 1
                bet_amount = bet_amount0 * (heso ** stats['lose_streak'])

                cycle = delay1 + delay2
                pos = (tong_van - 1) % cycle if cycle > 0 else 0
                is_resting = pos >= delay1
                
                if not is_resting and random.random() < 0.05:
                    rest_msg = f"[yellow]💤 Bỏ qua ván này ngẫu nhiên để thay đổi hành vi.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                if is_resting:
                    rest_msg = f"[yellow]💤 Tạm nghỉ. Tiếp tục sau {cycle - pos} ván nữa.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                pre_bet_delay = random.uniform(2, 5)
                time.sleep(pre_bet_delay)

                # =================== BẮT ĐẦU KHỐI LOGIC CƯỢC ĐÃ SỬA LỖI ===================

                # 1. Lấy ID phiên mới nhất ngay trước khi cược để tránh lỗi trễ thời gian
                final_check_id, _ = fetch_latest_issue_info(s, headers)
                if final_check_id is None:
                    add_log(logs, "[yellow]⚠️ Lỗi API, bỏ qua ván này[/yellow]")
                    time.sleep(5) # Chờ một chút trước khi thử lại
                    continue
                
                current_betting_issue_id = final_check_id + 1

                # 2. KIỂM TRA CHỐNG CƯỢC LẶP LẠI MỘT VÁN
                if current_betting_issue_id in attempted_bets:
                    log_msg = f"[yellow]⚠️ Đã thử cược ván #{current_betting_issue_id}. Bỏ qua cược lặp.[/yellow]"
                    add_log(logs, log_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, log_msg, key_info), refresh=True)
                    time.sleep(10) # Chờ để ván này chắc chắn trôi qua
                    continue

                # 3. GHI NHẬN LÀ ĐÃ CƯỢC VÁN NÀY (Ghi nhận trước khi gọi API)
                attempted_bets.append(current_betting_issue_id)

                # 4. Tiến hành lấy logic và đặt cược
                kq = logic_engine.analyze_and_select(current_betting_issue_id)
                response = bet_cdtd(s, headers, current_betting_issue_id, kq, Coin, bet_amount, logs)
                
                # 5. Xử lý kết quả trả về từ API cược
                if response and response.get('code') == 0:
                    start_wait_time = time.time()
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, current_betting_issue_id)
                        if result is not None: break
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"⏳ Đợi KQ kì #{current_betting_issue_id}: {elapsed}s '{NV.get(kq, kq)}'.      với [yellow]{bet_amount:,.4f} {Coin}[/yellow]"
                        live.update(generate_dashboard(config, stats, current_asset, logs, Coin, wait_message, key_info), refresh=True)
                        time.sleep(1)

                    if result: # THẮNG
                        stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"[bold green]THẮNG[/bold green] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[cyan]{NV.get(actual_winner, actual_winner)}[/cyan]'")
                    else: # THUA
                        stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        stats['consecutive_loss_counts'][stats['lose_streak']] += 1
                        log_msg = (f"[bold red]THUA[/bold red] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[red]{NV.get(actual_winner, actual_winner)}[/red]' (Trùng)")
                    add_log(logs, log_msg)
                
                else: # Xử lý khi cược không thành công
                    if response: # Nếu có phản hồi lỗi từ server (VD: "issue finished already")
                        log_msg = f"[red]Lỗi cược ván #{current_betting_issue_id}:[/red] [white]{response.get('msg', 'Không rõ lỗi')}[/white]"
                        add_log(logs, log_msg)
                    # Nếu `response` là `None`, lỗi mạng đã được log bên trong hàm bet_cdtd
                
                # Cập nhật giao diện lần cuối trước khi sang ván mới
                final_asset = user_asset(s, headers)
                live.update(generate_dashboard(config, stats, final_asset, logs, Coin, "", key_info), refresh=True)
                time.sleep(random.uniform(5, 10))

                # =================== KẾT THÚC KHỐI LOGIC CƯỢC ĐÃ SỬA LỖI ===================

            except Exception as e:
                import traceback; error_message = traceback.format_exc()
                add_log(logs, f"[bold red]Lỗi nghiêm trọng. Sẽ thử lại sau 10s[/bold red]")
                # with open("error_log.txt", "a", encoding="utf-8") as f:
                #     f.write(f"--- Lỗi lúc {datetime.now()} ---\n{error_message}\n")
                time.sleep(10)

def show_banner():
    clear_screen()
    banner_text = Text.from_markup(f"""
[bold cyan]
 ████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝
    ██║   ██║  ██║██╔═██╗
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝
[/bold cyan]
    """, justify="center")
    console.print(Panel(banner_text, border_style="magenta"))
    console.print(Align.center("[bold gold1]Tool VIP V8 - Khởi tạo thành công![/bold gold1]\n"))
    time.sleep(3)


if __name__ == "__main__":
    # Nâng cấp logic cần thư viện, thêm vào đây để tương thích
    try:
        import itertools
    except ImportError:
        os.system("pip install itertools")
        import itertools

    authentication_successful, device_id, key_info = main_authentication()

    if authentication_successful:
        show_banner()
        main_cdtd(device_id, key_info)
    else:
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()