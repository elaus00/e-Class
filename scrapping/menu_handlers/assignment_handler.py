from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class AssignmentMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        assignments = soup.select('.assignment-list-item')  # 가정된 CSS 선택자
        
        print("과제 목록:")
        for assignment in assignments:
            title = assignment.select_one('.assignment-title')
            due_date = assignment.select_one('.assignment-due-date')
            status = assignment.select_one('.assignment-status')
            if title and due_date and status:
                print(f"- {title.text.strip()} (마감일: {due_date.text.strip()}, 상태: {status.text.strip()})")
