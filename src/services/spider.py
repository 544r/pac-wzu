"""
温州大学教务系统爬虫模块
"""
import time
import base64
import requests
from http.cookiejar import Cookie
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WzuSpider:
    """温州大学教务系统爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False
        self.login_url = "https://source.wzu.edu.cn/login"
        self.service_url = "https://jwxt.wzu.edu.cn/sso/zfiotlogin"
        self.full_login_url = f"{self.login_url}?service={self.service_url}"
        self.home_url = "https://jwxt.wzu.edu.cn/jwglxt/xtgl/index_initMenu.html"
        self.grade_page_url = "https://jwxt.wzu.edu.cn/jwglxt/cjcx/cjcx_cxXsgrcj.html?gnmkdm=N305005&layout=default"
        self.grade_api_url = "https://jwxt.wzu.edu.cn/jwglxt/cjcx/cjcx_cxXsgrcj.html?doType=query&gnmkdm=N305005"

    def _aes_encrypt(self, password, key_base64):
        """AES加密密码（用于登录）"""
        try:
            key = base64.b64decode(key_base64)
            padded = pad(password.encode('utf-8'), AES.block_size)
            return base64.b64encode(AES.new(key, AES.MODE_ECB).encrypt(padded)).decode()
        except:
            return None

    def get_cookies_for_storage(self):
        """获取cookies用于存储"""
        return [
            {
                'name': c.name,
                'value': c.value,
                'domain': c.domain,
                'path': c.path,
                'secure': c.secure,
                'expires': c.expires
            }
            for c in self.session.cookies
        ]

    def load_cookies_from_storage(self, cookies_list):
        """从存储加载cookies"""
        for c in cookies_list:
            try:
                self.session.cookies.set_cookie(Cookie(
                    0, c['name'], c['value'], None, False,
                    c['domain'], bool(c['domain']),
                    c['domain'].startswith('.') if c['domain'] else False,
                    c['path'], bool(c['path']),
                    c['secure'], c['expires'], True, None, None, {}, False
                ))
            except:
                pass

    def login(self, username, password):
        """登录教务系统"""
        try:
            r = self.session.get(self.full_login_url, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 获取 execution 参数
            tag = soup.find('p', {'id': 'login-page-flowkey'})
            ex = tag.text.strip() if tag else ""
            if not ex:
                inp = soup.find('input', {'name': 'execution'})
                ex = inp.get('value') if inp else ""
            
            # 获取加密密钥
            ktag = soup.find('p', {'id': 'login-croypto'})
            key = ktag.text.strip() if ktag else ""
            
            if not ex or not key:
                return False, "无法获取登录参数"
            
            # 加密密码
            enc_pwd = self._aes_encrypt(password, key)
            if not enc_pwd:
                return False, "密码加密失败"
            
            # 提交登录
            lr = self.session.post(
                self.full_login_url,
                data={
                    'username': username,
                    'password': enc_pwd,
                    'type': 'UsernamePassword',
                    '_eventId': 'submit',
                    'geolocation': '',
                    'execution': ex,
                    'captcha_code': '',
                    'croypto': key
                },
                timeout=20
            )
            
            if "密码错误" in lr.text or "用户名或密码错误" in lr.text:
                return False, "账号或密码错误"
            
            if "jwxt.wzu.edu.cn" not in lr.url and ("统一身份认证" in lr.text or "login" in lr.url):
                return False, "登录失败"
            
            # 验证登录
            try:
                check = self.session.get(self.home_url, timeout=15, allow_redirects=False)
                if check.status_code != 200:
                    return False, "验证失败"
            except:
                return False, "验证超时"
            
            return True, "成功"
            
        except requests.Timeout:
            return False, "连接超时"
        except Exception as e:
            return False, str(e)

    def get_grades(self, xnm="", xqm=""):
        """获取成绩"""
        try:
            self.session.get(self.grade_page_url, timeout=15)
        except:
            pass
        
        try:
            r = self.session.post(
                self.grade_api_url,
                data={
                    'xnm': xnm,
                    'xqm': xqm,
                    '_search': 'false',
                    'nd': int(time.time() * 1000),
                    'queryModel.showCount': '500',
                    'queryModel.currentPage': '1',
                    'queryModel.sortOrder': 'asc',
                    'time': '0'
                },
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'Referer': self.grade_page_url
                },
                timeout=20
            )
            if r.status_code == 200:
                return True, r.json().get('items', [])
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)
