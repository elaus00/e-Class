from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

class TeamProjectMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        projects = soup.select('.team-project-item')  # 가정된 CSS 선택자
        
        print("팀 프로젝트 목록:")
        for project in projects:
            title = project.select_one('.project-title')
            deadline = project.select_one('.project-deadline')
            team = project.select_one('.project-team')
            if title and deadline and team:
                print(f"- {title.text.strip()} (마감일: {deadline.text.strip()}, 팀: {team.text.strip()})")
