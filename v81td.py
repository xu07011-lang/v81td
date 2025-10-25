import base64
import hashlib
import json
import os
import platform
import random
import re
import string
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

import itertools
from collections import Counter, defaultdict, deque

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    import pytz
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.align import Align
    from rich.text import Text
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "colorama", "pytz", "rich"])
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

console = Console()

FREE_CACHE_FILE = 'free_key_cache.json'
VIP_CACHE_FILE = 'vip_cache.json'
HANOI_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/keyxworkdf/main/keyxworkdf.txt"

def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
████████╗██████╗░██╗░░██╗
╚══██╔══╝██╔══██╗██║░██╔╝
░░░██║░░░██║░░██║█████═╝░
░░░██║░░░██║░░██║██╔═██╗░
░░░██║░░░██████╔╝██║░╚██╗
░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝
══════════════════════════
Admin: DUONG phung
Tool xworld VTD
TIKTOK: @tdktool
══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.0001)

def get_device_id():
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
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    authentication_banner()
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")

def save_vip_key_info(device_id, key, expiration_date_str):
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
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
        
def seeded_shuffle_js_equivalent(array, seed):
    seed_value = 0
    for i, char in enumerate(seed):
        seed_value = (seed_value + ord(char) * (i + 1)) % 1_000_000_000
    def custom_random():
        nonlocal seed_value
        seed_value = (seed_value * 9301 + 49297) % 233280
        return seed_value / 233280.0
    shuffled_array = array[:]
    current_index = len(shuffled_array)
    while current_index != 0:
        random_index = int(custom_random() * current_index)
        current_index -= 1
        shuffled_array[current_index], shuffled_array[random_index] = shuffled_array[random_index], shuffled_array[current_index]
    return shuffled_array

def save_free_key_info(device_id, key, expiration_date):
    data = {device_id: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(FREE_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)

def load_free_key_info():
    try:
        with open(FREE_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def check_saved_free_key(device_id):
    data = load_free_key_info()
    if data and device_id in data:
        try:
            expiration_date = datetime.fromisoformat(data[device_id]['expiration_date'])
            if expiration_date > datetime.now(HANOI_TZ):
                return data[device_id]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_free_key_and_url(device_id):
    today_str = datetime.now(HANOI_TZ).strftime('%Y-%m-%d')
    seed_str = f"TDK_FREE_KEY_{device_id}_{today_str}"
    hashed_seed = hashlib.sha256(seed_str.encode()).hexdigest()
    digits = [d for d in hashed_seed if d.isdigit()][:10]
    letters = [l for l in hashed_seed if 'a' <= l <= 'f'][:5]
    while len(digits) < 10:
        digits.extend(random.choices(string.digits))
    while len(letters) < 5:
        letters.extend(random.choices(string.ascii_lowercase))
    key_list = digits + letters
    shuffled_list = seeded_shuffle_js_equivalent(key_list, hashed_seed)
    key = "".join(shuffled_list)
    now_hanoi = datetime.now(HANOI_TZ)
    expiration_date = now_hanoi.replace(hour=21, minute=0, second=0, microsecond=0)
    url = f'https://tdkbumxkey.blogspot.com/2025/10/lay-link.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={urllib.parse.quote(url)}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"Lỗi {response.status_code}: Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(device_id):
    if datetime.now(HANOI_TZ).hour >= 21:
        print(f"{do}Đã qua 21:00 giờ Việt Nam, key miễn phí cho hôm nay đã hết hạn.{trang}")
        print(f"{vang}Vui lòng quay lại vào ngày mai để nhận key mới.{trang}")
        time.sleep(3)
        return False

    url, key, expiration_date = generate_free_key_and_url(device_id)
    shortened_data = get_shortened_link_phu(url)

    if shortened_data and shortened_data.get('status') == "error":
        print(f"{do}{shortened_data.get('message')}{trang}")
        return False

    link_key_shortened = shortened_data.get('shortenedUrl')
    if not link_key_shortened:
        print(f"{do}Không thể tạo link rút gọn. Vui lòng thử lại.{trang}")
        return False

    print(f'{trang}[{do}<>{trang}] {hong}Vui Lòng Vượt Link Để Lấy Key Free (Hết hạn 21:00 hàng ngày).{trang}')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_shortened}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            if datetime.now(HANOI_TZ) >= expiration_date:
                print(f"{do}Rất tiếc, key này đã hết hạn vào lúc 21:00. Vui lòng quay lại vào ngày mai.{trang}")
                return False
            time.sleep(2)
            save_free_key_info(device_id, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_shortened}{trang}')

def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)
    key_info = {'type': 'None', 'key': 'N/A', 'expiry': 'N/A'}

    if not device_id:
        print(f"{do}Không thể lấy thông tin Mã Máy. Vui lòng kiểm tra lại thiết bị.{trang}")
        return False, None, key_info

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
            print(f"{do}Lỗi file lưu key VIP. Vui lòng nhập lại key.{trang}")

    if check_saved_free_key(device_id):
        expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn (Hết hạn lúc {expiry_str}). Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': 'Active', 'expiry': expiry_str}
        time.sleep(2)
        return True, device_id, key_info

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Hết hạn 21:00 hàng ngày){trang}")
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
                if process_free_key(device_id):
                    expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
                    key_info = {'type': 'Free', 'key': 'Active', 'expiry': expiry_str}
                    return True, device_id, key_info
                else:
                    sleep(1)

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}
ALL_NV_IDS = list(NV.keys())

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

class LogicEngineV9:
    def __init__(self, state_manager, history_min_size=10):
        self.history = deque(maxlen=200)
        self.state_manager = state_manager
        self.history_min_size = history_min_size
        self.logics = self._get_all_logics()
        self.fallback_logic = lambda: random.choice(ALL_NV_IDS)

    def add_result(self, winner_id):
        if winner_id in NV:
            self.history.append(winner_id)

    def _get_all_logics(self):
        return [getattr(self, f"logic_{i:02}") for i in range(1, 51)]
    
    def logic_01(self): return Counter(self.history).most_common()[-1][0] if self.history else self.fallback_logic()
    def logic_02(self): return Counter(self.history).most_common(1)[0][0] if self.history else self.fallback_logic()
    def logic_03(self): return self.history[-1] if self.history else self.fallback_logic()
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
    def logic_11(self): return random.choice([c for c in ALL_NV_IDS if c != self.history[-1]]) if self.history else self.fallback_logic()
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
        runs = [len(list(g)) for k, g in itertools.groupby(self.history)] if self.history else []
        avg_run = round(sum(runs) / len(runs)) if runs else 1
        return avg_run if 1 <= avg_run <= 6 else 1
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
        if len(self.history) < 2: return self.logic_04()
        last_seen = {val: i for i, val in enumerate(self.history)}
        if not last_seen: return 6
        sorted_seen = sorted(last_seen.items(), key=lambda item: item[1], reverse=True)
        return sorted_seen[1][0] if len(sorted_seen) > 1 else sorted_seen[0][0]
    def logic_36(self): return (self.logic_13() + self.logic_14()) % 6 + 1
    def logic_37(self):
        s = set(self.history)
        return sorted(list(s))[0] if s else 1
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
    def logic_47(self):
        counts = Counter(self.history).most_common()
        return counts[-2][0] if len(counts) > 1 else self.logic_01()
    def logic_48(self):
        counts = Counter(self.history).most_common()
        return counts[1][0] if len(counts) > 1 else self.logic_02()
    def logic_49(self):
        return (self.history[-1] + self.history[-2]) % 6 + 1 if len(self.history) > 1 else self.logic_01()
    def logic_50(self): return random.choice(ALL_NV_IDS)

    def analyze_and_select(self, issue_id):
        if len(self.history) < self.history_min_size:
            candidate = self.fallback_logic()
            top6_char = -1
        else:
            selected_logic = self.logics[issue_id % len(self.logics)]
            candidate = selected_logic()

            frequencies = Counter(self.history)
            full_frequencies = {char_id: frequencies.get(char_id, 0) for char_id in ALL_NV_IDS}
            top6_char = min(full_frequencies, key=full_frequencies.get)
            
            if candidate == top6_char:
                alternative_choices = [c for c in ALL_NV_IDS if c != top6_char]
                if alternative_choices:
                    candidate = random.choice(alternative_choices)
                else:
                    candidate = self.fallback_logic()
    
        shared_bets = self.state_manager.get_shared_bets(issue_id)
        claimed_chars = [int(k) for k in shared_bets.keys()]

        if candidate not in claimed_chars:
            self.state_manager.claim_bet(issue_id, candidate)
            return candidate
        else:
            available_options = [c for c in ALL_NV_IDS if c not in claimed_chars]

            if not available_options:
                return self.fallback_logic()

            preferred_options = [opt for opt in available_options if opt != top6_char]

            final_choice = None
            if preferred_options:
                final_choice = random.choice(preferred_options)
            else:
                final_choice = random.choice(available_options)
                
            self.state_manager.claim_bet(issue_id, final_choice)
            return final_choice

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
    
    key_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    key_table.add_column(style="cyan"); key_table.add_column(style="white")
    
    if key_info.get('type') == 'VIP':
        key_table.add_row("Loại Key", "[bold gold1]VIP[/bold gold1]")
        key_table.add_row("Key", f"[gold1]{key_info.get('key', 'N/A')}[/gold1]")
        key_table.add_row("Hạn Dùng", f"[yellow]{key_info.get('expiry', 'N/A')}[/yellow]")
    elif key_info.get('type') == 'Free':
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(hcm_tz)
        expiry_time_today = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if expiry_time_today < now:
            expiry_time = now + timedelta(days=1)
            expiry_time = expiry_time.replace(hour=21, minute=0, second=0, microsecond=0)
            expiry_text = "[green]Key đã hết hạn. Hạn mới 21:00 ngày mai[/green]"
        else:
            expiry_time = expiry_time_today
            expiry_text = "[green]21:00:00 hàng ngày[/green]"
        
        delta = expiry_time - now
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        key_table.add_row("Loại Key", "[bold green]Free[/bold green]")
        key_table.add_row("Hết hạn vào", expiry_text)
        key_table.add_row("Thời gian còn", f"[yellow]{countdown}[/yellow]")
    
    key_panel = Panel(key_table, title="[bold]Thông Tin Key[/bold]", border_style="blue")

    info_layout = Table.grid(expand=True)
    info_layout.add_column(ratio=1); info_layout.add_column(ratio=1)
    info_layout.add_row(Panel(stats_table, title="[bold]Thống Kê[/bold]", border_style="blue"), Panel(config_table, title="[bold]Cấu Hình[/bold]", border_style="blue"))
    info_layout.add_row(Panel(balance_table, border_style="blue"), key_panel)

    log_panel = Panel("\n".join(reversed(logs)), title="[bold]Nhật Ký Hoạt Động[/bold]", border_style="green", height=12)
    
    status_panel = Panel(Align.center(Text(status_message, justify="center")), title="[bold]Trạng Thái[/bold]", border_style="yellow", height=3)
    
    main_grid = Table.grid(expand=True)
    main_grid.add_row(status_panel)
    main_grid.add_row(info_layout)
    main_grid.add_row(log_panel)
    
    dashboard = Panel(
        main_grid,
        title=f"[bold gold1]VTD V8[/bold gold1] - Thời gian chạy: {format_time(time.time() - config['start_time'])}",
        border_style="bold magenta"
    )
    return dashboard

def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        console.print(f"[cyan]Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): [/cyan]", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(f"\n[yellow]Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây[/yellow]")
    console.print(f"[cyan]📋 Vui lòng nhập link của bạn: [/cyan]", end=''); link = input()
    try:
        user_id = re.search(r'userId=(\d+)', link).group(1)
        secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    except AttributeError:
        console.print(f"[bold red]❌ Link không hợp lệ hoặc thiếu thông tin User ID/Secret Key.[/bold red]")
        sys.exit()
    
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
    while True:
        try:
            json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
            return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
        except Exception as e:
            console.print(f"[red]Lỗi khi lấy số dư: {e}. Thử lại sau 2s...[/red]"); time.sleep(2)

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount, logs):
    try:
        bet_amount_randomized = round(bet_amount * random.uniform(0.995, 1.005), 8)
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': bet_amount_randomized}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        
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
    
    SHARED_API_ENDPOINT = "https://api.jsonblob.com/api/jsonBlob/1286918519102373888"
    user_unique_id = hashlib.sha256(device_id.encode()).hexdigest()[:8]
    state_manager = SharedStateManager(SHARED_API_ENDPOINT, user_unique_id)
    logic_engine = LogicEngineV9(state_manager)

    stats = {
        'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 
        'asset_0': asset.get(Coin, 0), 'consecutive_loss_counts': defaultdict(int)
    }
    config = {'bet_amount0': bet_amount0, 'heso': heso, 'delay1': delay1, 'delay2': delay2, 'start_time': time.time()}
    logs = deque(maxlen=10); tong_van = 0
    
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

                final_check_id, _ = fetch_latest_issue_info(s, headers)
                if final_check_id is None:
                    add_log(logs, "[yellow]⚠️ Lỗi API, bỏ qua ván này[/yellow]")
                    time.sleep(5)
                    continue
                
                current_betting_issue_id = final_check_id + 1

                if current_betting_issue_id in attempted_bets:
                    log_msg = f"[yellow]⚠️ Đã thử cược ván #{current_betting_issue_id}. Bỏ qua cược lặp.[/yellow]"
                    add_log(logs, log_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, log_msg, key_info), refresh=True)
                    time.sleep(10)
                    continue

                attempted_bets.append(current_betting_issue_id)

                kq = logic_engine.analyze_and_select(current_betting_issue_id)
                response = bet_cdtd(s, headers, current_betting_issue_id, kq, Coin, bet_amount, logs)
                
                if response and response.get('code') == 0:
                    start_wait_time = time.time()
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, current_betting_issue_id)
                        if result is not None: break
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"⏳ Đợi KQ kì #{current_betting_issue_id}: {elapsed}s '{NV.get(kq, kq)}'.      với [yellow]{bet_amount:,.4f} {Coin}[/yellow]"
                        live.update(generate_dashboard(config, stats, current_asset, logs, Coin, wait_message, key_info), refresh=True)
                        time.sleep(1)

                    if result:
                        stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"[bold green]THẮNG[/bold green] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[cyan]{NV.get(actual_winner, actual_winner)}[/cyan]'")
                    else:
                        stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        stats['consecutive_loss_counts'][stats['lose_streak']] += 1
                        log_msg = (f"[bold red]THUA[/bold red] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[red]{NV.get(actual_winner, actual_winner)}[/red]' (Trùng)")
                    add_log(logs, log_msg)
                
                else:
                    if response:
                        log_msg = f"[red]Lỗi cược ván #{current_betting_issue_id}:[/red] [white]{response.get('msg', 'Không rõ lỗi')}[/white]"
                        add_log(logs, log_msg)
                
                final_asset = user_asset(s, headers)
                live.update(generate_dashboard(config, stats, final_asset, logs, Coin, "", key_info), refresh=True)
                time.sleep(random.uniform(5, 10))

            except Exception as e:
                add_log(logs, f"[bold red]Lỗi nghiêm trọng. Sẽ thử lại sau 10s[/bold red]")
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
    console.print(Align.center("[bold gold1]CHẠY ĐUA V8 - Khởi tạo thành công![/bold gold1]\n"))
    time.sleep(3)


if __name__ == "__main__":
    authentication_successful, device_id, key_info = main_authentication()

    if authentication_successful:
        show_banner()
        main_cdtd(device_id, key_info)
    else:
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()
