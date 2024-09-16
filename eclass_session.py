import configparser
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
import json
from dataclasses import dataclass
from enum import Enum, auto

from config import BASE_URL, LOGIN_URL, MAIN_URL, COURSE_ACCESS_URL, SUBMAIN_URL

@dataclass
class Course:
    id: str
    name: str
    code: str
    time: str

class MenuType(Enum):
    PLAN = auto()
    ONLINE_LECTURE = auto()
    NOTICE = auto()
    LECTURE_MATERIAL = auto()
    ATTENDANCE = auto()
    ASSIGNMENT = auto()
    TEAM_PROJECT = auto()
    EXAM = auto()

class EclassSession:
    def __init__(self, config_path: str = 'config.ini'):
        self.session = requests.Session()
        self.config = self._load_config(config_path)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'credentials' not in config:
            raise ValueError("설정 파일에 'credentials' 섹션이 없습니다.")
        return config

    def login(self) -> bool:
        username = self.config['credentials']['username']
        password = self.config['credentials']['password']
        login_data = {
            "usr_id": username,
            "usr_pwd": password,
            "returnURL": "",
        }
        try:
            response = self.session.post(LOGIN_URL, data=login_data, headers=self.headers)
            response.raise_for_status()
            if "document.location.href=" in response.text or "main_form.acl" in response.text:
                logging.info("로그인 성공")
                return True
            else:
                logging.error("로그인 실패")
                return False
        except requests.RequestException as e:
            logging.error(f"로그인 중 오류 발생: {e}")
            return False

    def get_course_list(self) -> List[Course]:
        try:
            response = self.session.get(MAIN_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            course_elements = soup.find_all('li', style=lambda value: value and 'background: url' in value)
            
            return [self._parse_course_element(element) for element in course_elements if self._parse_course_element(element)]
        except requests.RequestException as e:
            logging.error(f"과목 목록 가져오기 중 오류 발생: {e}")
            return []

    def _parse_course_element(self, element: BeautifulSoup) -> Optional[Course]:
        name_elem = element.find('em', class_='sub_open')
        if not name_elem:
            return None

        course_id = name_elem.get('kj')
        full_name = name_elem.text.strip()
        name_parts = full_name.rsplit('(', 1)
        course_name = name_parts[0].strip()
        course_code = name_parts[1].strip(') ') if len(name_parts) > 1 else ''
        
        time_elem = element.find('span')
        course_time = time_elem.text.strip() if time_elem else ''
        
        return Course(id=course_id, name=course_name, code=course_code, time=course_time)

    def access_course(self, course_id: str) -> Optional[str]:
        data = {
            "KJKEY": course_id,
            "returnData": "json",
            "returnURI": SUBMAIN_URL,
            "encoding": "utf-8"
        }
        try:
            response = self.session.post(COURSE_ACCESS_URL, data=data)
            response.raise_for_status()
            json_data = response.json()
            if json_data.get('isError'):
                logging.error(f"과목 접근 실패: {json_data.get('message')}")
                return None
            return json_data.get('returnURL')
        except (requests.RequestException, json.JSONDecodeError) as e:
            logging.error(f"과목 접근 중 오류 발생: {e}")
            return None

    def get_course_menus(self, course_id: str) -> Dict[MenuType, Dict[str, str]]:
        access_url = self.access_course(course_id)
        if not access_url:
            return {}

        try:
            response = self.session.get(access_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._get_specific_menus(soup)
        except requests.RequestException as e:
            logging.error(f"과목 메뉴 가져오기 중 오류 발생: {e}")
            return {}

    def _get_specific_menus(self, soup: BeautifulSoup) -> Dict[MenuType, Dict[str, str]]:
        menus = {}
        menu_mapping = {
            'st_plan': MenuType.PLAN,
            'st_onlineclass': MenuType.ONLINE_LECTURE,
            'st_notice': MenuType.NOTICE,
            'st_lecture_material': MenuType.LECTURE_MATERIAL,
            'st_attendance': MenuType.ATTENDANCE,
            'st_report': MenuType.ASSIGNMENT,
            'st_teamproject': MenuType.TEAM_PROJECT,
            'st_exam': MenuType.EXAM
        }

        menu_items = soup.find_all('li', class_='course_menu_item')
        for item in menu_items:
            menu_id = item.get('id', '')
            if menu_id in menu_mapping:
                link = item.find('a')
                if link:
                    menu_name = link.text.strip()
                    menu_url = link['href']
                    menus[menu_mapping[menu_id]] = {
                        'name': menu_name,
                        'url': f"{BASE_URL}{menu_url}" if menu_url.startswith('/') else menu_url
                    }
        return menus

    def get_page_content(self, url: str) -> str:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"페이지 내용 가져오기 중 오류 발생: {e}")
            return ""