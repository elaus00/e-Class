import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlencode
from datetime import datetime
from scrapping.eclass_session import EclassSession
import json

class SeleniumScraper:
    def __init__(self):
        self.eclass_session = EclassSession()
        self.chrome_driver_path = r"C:\Users\elaus\Chrome\chromedriver-win32\chromedriver.exe"
        self.driver = None

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('window-size=0x0')
        chrome_options.add_argument("disable-gpu")
        service = Service(self.chrome_driver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _handle_popups(self):
        main_window = self.driver.current_window_handle
        for handle in self.driver.window_handles:
            if handle != main_window:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(main_window)

    def _login(self, login_url):
        self.driver.get(login_url)
        self._handle_alert()
        
        try:
            username_field = self.driver.find_element(By.ID, "usr_id")
            username_field.clear()
            username_field.send_keys(self.eclass_session.username)
            
            password_field = self.driver.find_element(By.ID, "usr_pwd")
            password_field.clear()
            password_field.send_keys(self.eclass_session.password)

            login_button = self.driver.find_element(By.XPATH, "//input[@type='image' and @alt='확인']")
            login_button.click()
        except NoSuchElementException as e:
            raise

    def _handle_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass

    def get_page(self, url):
        try:
            self.driver.get(url)
            return self.driver.page_source
        except Exception as e:
            return None

    def scrape(self, params, parsed_params, list_view_url):
        session_info = self.eclass_session.get_detailed_session_info()

        ky_code = params.get('ky', '')
        if not ky_code:
            raise ValueError("KY code is missing or empty. Cannot enter the class room.")

        try:
            self.driver = self._setup_driver()
            self._login(session_info['login_url'])

            ajax_script = """
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/ilos/st/course/eclass_room2.acl', false);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('KJKEY={ky}&returnData=json&returnURI=/ilos/st/course/submain_form.acl&encoding=utf-8');
            return xhr.responseText;
            """.format(ky=ky_code)

            response_text = self.driver.execute_script(ajax_script)
            
            response_data = json.loads(response_text)
            if response_data.get('isError'):
                raise Exception(response_data.get('message'))
            
            return_url = response_data.get('returnURL')
            if not return_url:
                raise Exception("No return URL provided in the response")

            ordered_params = [
                ('ARTL_NUM', parsed_params.get('ARTL_NUM', '')),
                ('SCH_KEY', params.get('SCH_KEY', '')),
                ('SCH_VALUE', params.get('SCH_VALUE', '')),
                ('display', params.get('display', '1')),
                ('start', params.get('start', '1'))
            ]
            encoded_params = '&'.join(f"{k}={urlencode({k: str(v)}).split('=')[1]}" for k, v in ordered_params)
            lecture_material_url = f"{list_view_url}?{encoded_params}"

            page_source = self.get_page(lecture_material_url)
            return page_source
        except Exception as e:
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def save_debug_html(self, html_content, base_filename):
        debug_dir = 'debug'
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.html"
        filepath = os.path.join(debug_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("<!-- This file is created for debugging purposes. -->\n")
            f.write(html_content)