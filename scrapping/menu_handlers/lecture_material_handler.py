from config import BASE_URL
from scrapping.eclass_session import EclassSession
from utils.html_parser import HTMLParser
from utils.list_handler import fetch_and_parse_list
from utils.display_handler import display_list_and_navigate
from typing import List, Dict, Optional

class LectureMaterialMenuHandler:    
    def __init__(self, session: EclassSession, course_id: str):
        self.session = session
        self.course_id = course_id
        self.username = session.username
        self.html_parser = HTMLParser()

    def get_lecture_material_list(self, start: int = 1, search_value: str = '') -> Optional[List[Dict[str, str]]]:
        list_url = f"{BASE_URL}/ilos/st/course/lecture_material_list.acl"
        params = {
            'start': str(start),
            'display': '1',
            'SCH_VALUE': search_value,
            'ud': self.username,
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        
        materials = fetch_and_parse_list(
            url=list_url,
            params=params,
            post_request=self.session.post_request,
            display_list=None,
            save_filename="강의자료 리스트.html",
        )

        if materials:
            self._display_materials(materials)

        return materials

    def _display_materials(self, materials: List[Dict[str, str]]) -> None:
        display_list_and_navigate(
            items=materials,
            get_content=self.session.get_request,
            clean_content=HTMLParser.clean_content,
            title="강의 자료 목록",
            item_type="강의자료"
        )

    def handle(self, menu_data: Dict[str, str] = None) -> None:
        self.get_lecture_material_list()