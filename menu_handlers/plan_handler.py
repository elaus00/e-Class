from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict

# 강의계획서
class PlanMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        content = self.session.get_page_content(menu_data['url'])
        soup = BeautifulSoup(content, 'html.parser')
        
        plan_info = self._extract_plan_info(soup)
        
        if plan_info:
            print("강의계획서 정보:")
            for key, value in plan_info.items():
                print(f"{key}: {value}")
        else:
            print("강의계획서 정보를 찾을 수 없습니다.")

    def _extract_plan_info(self, soup):
        plan_info = {}
        
        # 기본 정보 추출
        table = soup.find('tbody')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) == 6:
                    plan_info['년도/학기'] = cells[1].text.strip()
                    plan_info['교과목명'] = cells[3].text.strip()
                    plan_info['교과목번호/강좌번호'] = cells[5].text.strip()
                    break  # 첫 번째 행에서 필요한 정보를 모두 얻었으므로 반복 중단
        
        # 추가 정보 추출 (예: 교수명, 학점 등)
        # 실제 HTML 구조에 따라 이 부분을 수정해야 할 수 있습니다.
        # plan_info['교수명'] = soup.find('div', class_='professor-name').text.strip()
        # plan_info['학점'] = soup.find('div', class_='course-credit').text.strip()
        
        # 주차별 계획 추출
        # 주차별 계획 테이블의 실제 구조에 따라 이 부분을 수정해야 합니다.
        weekly_plan = soup.find('table', class_='weekly-plan')
        if weekly_plan:
            plan_info['주차별 계획'] = {}
            for row in weekly_plan.find_all('tr')[1:]:  # 헤더 제외
                cols = row.find_all('td')
                if len(cols) >= 2:
                    week = cols[0].text.strip()
                    content = cols[1].text.strip()
                    plan_info['주차별 계획'][week] = content
        
        return plan_info
