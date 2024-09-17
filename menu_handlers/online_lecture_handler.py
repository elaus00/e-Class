from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class OnlineLectureMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        lectures = soup.select('.lecture-list-item')  # 가정된 CSS 선택자
        
        print("온라인 강의 목록:")
        for lecture in lectures:
            title = lecture.select_one('.lecture-title')
            date = lecture.select_one('.lecture-date')
            if title and date:
                print(f"- {title.text.strip()} (날짜: {date.text.strip()})")
