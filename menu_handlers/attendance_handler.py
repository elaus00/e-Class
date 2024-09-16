from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class AttendanceMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        attendance_records = soup.select('.attendance-record')  # 가정된 CSS 선택자
        
        print("출석 현황:")
        for record in attendance_records:
            date = record.select_one('.attendance-date')
            status = record.select_one('.attendance-status')
            if date and status:
                print(f"- {date.text.strip()}: {status.text.strip()}")
