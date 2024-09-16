from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class LectureMaterialMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        materials = soup.select('.material-list-item')  # 가정된 CSS 선택자
        
        print("강의 자료 목록:")
        for material in materials:
            title = material.select_one('.material-title')
            date = material.select_one('.material-date')
            if title and date:
                print(f"- {title.text.strip()} (업로드 날짜: {date.text.strip()})")
