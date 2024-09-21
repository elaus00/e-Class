from .base import MenuHandler
from config import BASE_URL, get_config
from typing import Dict
from scrapping.eclass_session import EclassSession
from utils.html_parser import HTMLParser
from utils.list_handler import fetch_and_parse_list
from utils.display_handler import display_list_and_navigate
from utils.file_handler import save_html_content

class NoticeMenuHandler(MenuHandler):
    def __init__(self, session: EclassSession, course_id: str):
        self.session = session
        self.course_id = course_id
        self.config = get_config()
        self.html_parser = HTMLParser()

    def handle(self, menu_data: Dict[str, str] = None) -> None:
        self._handle_notices()

    def _handle_notices(self) -> None:
        notice_url = f"{BASE_URL}/ilos/st/course/notice_list.acl"
        params = {
            'start': '1',
            'display': '1',
            'SCH_VALUE': '',
            'ud': self.config['credentials']['username'],
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        
        notices = fetch_and_parse_list(
            url=notice_url,
            params=params,
            post_request=self.session.post_request,
            display_list=None,
            save_filename="공지사항 리스트.html",
        )

        if notices:
            display_list_and_navigate(
                items=notices,
                get_content=self.session.get_request,
                clean_content=HTMLParser.clean_content,
                title="공지사항 목록",
                item_type="공지사항"
            )
        else:
            print("공지사항이 없습니다.")