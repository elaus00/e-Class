from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class ExamMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        exams = soup.select('.exam-list-item')  # 가정된 CSS 선택자
        
        print("시험 일정:")
        for exam in exams:
            title = exam.select_one('.exam-title')
            date = exam.select_one('.exam-date')
            time = exam.select_one('.exam-time')
            if title and date and time:
                print(f"- {title.text.strip()} (날짜: {date.text.strip()}, 시간: {time.text.strip()})")