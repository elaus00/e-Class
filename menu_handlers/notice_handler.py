from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict, List, Optional

class NoticeMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        items = soup.select('.boardlist')
        for item in items:
            title = item.select_one('.title')
            date = item.select_one('.date')
            if title and date:
                print(f"- {title.text.strip()} ({date.text.strip()})")
