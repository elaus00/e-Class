from config import BASE_URL
from scrapping.eclass_session import EclassSession
from utils.html_parser import HTMLParser
from utils.list_handler import fetch_and_parse_list
from utils.display_handler import display_list_and_navigate
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

class LectureMaterialMenuHandler:    
    def __init__(self, session: EclassSession, course_id: str):
        self.session = session
        self.course_id = course_id
        self.username = session.username
        self.html_parser = HTMLParser()
        self.logger = self._setup_logger()

    # 로거 설정을 위한 내부 메소드
    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('lecture_material_handler.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    # 메인 핸들러 메소드: 강의 자료 목록 가져오기 프로세스 시작
    def handle(self, menu_data: Dict[str, str] = None) -> None:
        self.logger.info("강의 자료 메뉴 처리 시작")
        self.get_lecture_material_list()

    # 강의 자료 목록을 가져오고 처리하는 메소드
    def get_lecture_material_list(self, start: int = 1, search_value: str = '') -> Optional[Tuple[List[Dict[str, str]], Dict[str, str]]]:
        self.logger.info("강의 자료 목록 가져오기 시작")
        list_url = f"{BASE_URL}/ilos/st/course/lecture_material_list.acl"
        
        params = {
            'start': str(start),
            'display': '1',
            'SCH_VALUE': search_value,
            'ud': self.username,
            'ky': self.course_id,
            'encoding': 'utf-8'
        }

        # 강의 자료 목록 가져오기
        lecture_material_list, parsed_params = fetch_and_parse_list(
            session=self.session,
            url=list_url,
            params=params,
            save_filename=f"lecture_material_debug_{datetime.now().strftime('%Y%m%d')}.html",
        )

        # 강의 자료 목록 표시
        display_list_and_navigate(
            items=lecture_material_list,
            get_content=self.session.get_request,
            clean_content=self.html_parser.clean_content,
            title="강의 자료 목록",
            item_type="강의 자료",
            params = params,
            parsed_params=parsed_params,
        )
        
        # 첨부 파일 처리
        
        return lecture_material_list
