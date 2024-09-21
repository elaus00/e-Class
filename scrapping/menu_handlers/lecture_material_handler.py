from bs4 import BeautifulSoup
from .base import MenuHandler
from config import BASE_URL
from typing import Dict, List
import logging

class LectureMaterialMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        materials = self.get_lecture_materials()
        self.print_lecture_materials(materials)

    def get_lecture_materials(self) -> List[Dict[str, str]]:
        list_url = f"{BASE_URL}/st/course/lecture_material_list_form.acl"
        params = {
            'start': '',
            'display': '1',
            'SCH_VALUE': '',
            'ud': self.session.username,
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        content = self.session.get_page_content(list_url, method="POST", data=params)
        return self.parse_materials(content)

    def parse_materials(self, content: str) -> List[Dict[str, str]]:
            soup = BeautifulSoup(content, 'html.parser')
            material_rows = soup.select('table.bbslist > tbody > tr')
            
            logging.info(f"파싱된 강의 자료 행 수: {len(material_rows)}")
            
            if not material_rows:
                logging.warning("강의 자료 테이블을 찾을 수 없습니다. HTML 내용:")
                logging.warning(content[:500])  # HTML 내용의 일부만 로깅

            materials = []
            for i, row in enumerate(material_rows):
                columns = row.select('td')
                if len(columns) >= 4:
                    article_num = row.get('id', '').split('_')[-1]
                    material = {
                        'number': columns[0].text.strip(),
                        'title': columns[1].text.strip(),
                        'date': columns[2].text.strip(),
                        'file': columns[3].text.strip(),
                        'details': self.get_material_details(article_num)
                    }
                    materials.append(material)
                    logging.info(f"파싱된 강의 자료 {i+1}: {material['title']}")
                else:
                    logging.warning(f"행 {i+1}에 충분한 열이 없습니다: {len(columns)} 열 발견")

            logging.info(f"총 파싱된 강의 자료 수: {len(materials)}")
            return materials

    def get_lecture_materials(self) -> List[Dict[str, str]]:
        list_url = f"{BASE_URL}/st/course/lecture_material_list.acl"
        params = {
            'start': '',
            'display': '1',
            'SCH_VALUE': '',
            'ud': self.session.username,
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        content = self.session.get_page_content(list_url, method="POST", data=params)
        
        logging.info("강의 자료 목록 HTML 내용 일부:")
        logging.info(content[:500])  # HTML 내용의 일부만 로깅
        
        return self.parse_materials(content)

    def print_lecture_materials(self, materials: List[Dict[str, str]]) -> None:
        if not materials:
            logging.info("강의 자료가 없습니다.")
            return

        logging.info("강의 자료 목록:")
        for material in materials:
            logging.info(f"- [{material['number']}] {material['title']} (업로드 날짜: {material['date']}, 파일: {material['file']})")
            logging.info(f"  내용: {material['details']['content'][:100]}...")
            if material['details']['attachments']:
                logging.info(f"  첨부파일: {', '.join(material['details']['attachments'])}")
            logging.info("")