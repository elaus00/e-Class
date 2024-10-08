import configparser
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import logging
import json
from dataclasses import dataclass
from enum import Enum, auto
import asyncio
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
        self.user_id = None
        self.session = None  # 세션 초기화 지연
        self.config = self._load_config(config_path)
        self.username = self.config['credentials']['username']
        self.password = self.config['credentials']['password']

    async def init_session(self):
        # 이벤트 루프 내에서 세션 초기화
        self.session = aiohttp.ClientSession(headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'credentials' not in config:
            raise ValueError("설정 파일에 'credentials' 섹션이 없습니다.")
        return config

    async def login(self) -> bool:
        if self.session is None:
            await self.init_session()  # 세션 초기화
        
        login_data = {
            "usr_id": self.username,
            "usr_pwd": self.password,
            "returnURL": "",
        }
        try:
            async with self.session.post(LOGIN_URL, data=login_data) as response:
                if response.status != 200:
                    return False
                text = await response.text()
                if "document.location.href=" in text or "main_form.acl" in text:
                    self.user_id = self.username  # 로그인 성공 시 user_id 설정
                    return True
                else:
                    return False
        except aiohttp.ClientError as e:
            logging.error(f"로그인 중 오류 발생: {e}")
            return False


    def get_user_id(self):
        return self.user_id

    async def get_course_list(self) -> List[Course]:
        try:
            async with self.session.get(MAIN_URL) as response:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                course_elements = soup.find_all('li', style=lambda value: value and 'background: url' in value)
                return [self._parse_course_element(element) for element in course_elements if self._parse_course_element(element)]
        except aiohttp.ClientError as e:
            logging.error(f"과목 목록 가져오기 중 오류 발생: {e}")
            return []
        
    async def post_request(self, url: str, data: Dict[str, Any], headers=None) -> str:
        """
        지정된 URL로 POST 요청을 보내고 응답 내용을 반환합니다.

        :param url: POST 요청을 보낼 URL
        :param data: POST 요청에 포함할 데이터 딕셔너리
        :return: 응답 내용 (문자열)
        """
        try:
            async with self.session.post(url, data=data, headers=headers) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logging.error(f"POST 요청 중 오류 발생: {e}")
            return ""

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

    async def access_course(self, course_id: str) -> Optional[str]:
        data = {
            "KJKEY": course_id,
            "returnData": "json",
            "returnURI": SUBMAIN_URL,
            "encoding": "utf-8"
        }
        try:
            async with self.session.post(COURSE_ACCESS_URL, data=data) as response:
                response.raise_for_status()
                json_data = await response.json()
                if json_data.get('isError'):
                    logging.error(f"과목 접근 실패: {json_data.get('message')}")
                    return None
                return json_data.get('returnURL')
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            logging.error(f"과목 접근 중 오류 발생: {e}")
            return None

    async def get_course_menus(self, course_id: str) -> Dict[MenuType, Dict[str, str]]:
        access_url = await self.access_course(course_id)
        if not access_url:
            return {}

        try:
            async with self.session.get(access_url) as response:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                return self._get_specific_menus(soup)
        except aiohttp.ClientError as e:
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

    async def get_page_content(self, url: str, method: str = "GET", data: dict = None) -> str:
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, data=data) as response:
                    response.raise_for_status()
                    return await response.text()
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드입니다: {method}")
        except aiohttp.ClientError as e:
            logging.error(f"페이지 내용 가져오기 중 오류 발생: {e}")
            return ""
        
    async def get_request(self, url: str) -> str:
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logging.error(f"GET 요청 중 오류 발생: {e}")
            return ""
    
    async def head(self, url: str, params: Dict[str, Any] = None) -> aiohttp.ClientResponse:
        """
        지정된 URL로 HEAD 요청을 보내고 응답을 반환합니다.

        :param url: HEAD 요청을 보낼 URL
        :param params: 요청에 포함할 매개변수 딕셔너리 (선택사항)
        :return: aiohttp.ClientResponse 객체
        """
        try:
            async with self.session.head(url, params=params) as response:
                response.raise_for_status()
                return response
        except aiohttp.ClientError as e:
            logging.error(f"HEAD 요청 중 오류 발생: {e}")
            raise
        
    async def close_session(self):
        if self.session:
            await self.session.close()