import os
from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict, Any
from config import BASE_URL

# 강의계획서
class PlanMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        plan_view_url = f"{BASE_URL}/ilos/st/course/plan_view.acl"
        data = {
            'SCH_PROF': menu_data.get('SCH_PROF', ''),
            'encoding': 'utf-8'
        }
        content = self.session.post_request(plan_view_url, data)
        soup = BeautifulSoup(content, 'html.parser')
        
        plan_info = self._extract_plan_info(soup)
        
        if plan_info:
            text_content = self._generate_text(plan_info)
            success = self._save_text_to_file(text_content, menu_data.get('SCH_PROF', 'unknown'))
            if success:
                self._print_plan_info(plan_info)
            else:
                print("강의계획서 파일 저장에 실패했습니다.")
        else:
            print("강의계획서 정보를 찾을 수 없습니다.")

    def _extract_plan_info(self, soup):
        plan_info = {
            '[수업기본정보]': {},
            '[담당교수정보]': {},
            '[강의계획]': {},
            '[주별강의계획]': []
        }
        
        sections = soup.find_all('div', style=lambda value: value and 'padding-top' in value and 'font-weight: bold' in value)
        
        for section in sections:
            section_title = section.text.strip()
            if section_title in plan_info:
                table = section.find_next('table')
                if table:
                    if section_title != '[주별강의계획]':
                        self._extract_table_info(table, plan_info[section_title])
                    else:
                        self._extract_weekly_plan(table, plan_info[section_title])
        
        return plan_info

    def _extract_table_info(self, table, info_dict):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                info_dict[key] = value

    def _extract_weekly_plan(self, table, weekly_plan):
        rows = table.find_all('tr')[1:]  # 헤더 제외
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                week = cols[0].text.strip()
                content = cols[1].text.strip()
                note = cols[2].text.strip()
                if week and content:  # 빈 행 제외
                    weekly_plan.append({
                        '주차': week,
                        '내용': content,
                        '비고': note
                    })

    def _generate_text(self, plan_info: Dict[str, Any]) -> str:
        text = "강의계획서 정보\n\n"
        
        for section, content in plan_info.items():
            text += f"{section}\n\n"
            if isinstance(content, dict):
                for key, value in content.items():
                    text += f"{key}: {value}\n"
                text += "\n"
            elif isinstance(content, list):
                for item in content:
                    text += f"{item['주차']}. {item['내용']}\n"
                    if item['비고']:
                        text += f"   비고: {item['비고']}\n"
                text += "\n"
        
        return text

    def _save_text_to_file(self, text_content: str, course_id: str) -> bool:
        try:
            print("파일 저장 시작")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"현재 디렉토리: {current_dir}")

            # 상대 경로로 export 디렉토리 찾기 시도
            relative_export_dir = os.path.join(current_dir, '..', 'export')
            if os.path.exists(os.path.dirname(relative_export_dir)):
                export_dir = relative_export_dir
                print(f"상대 경로 사용: {export_dir}")
            else:
                # 상대 경로 실패 시 절대 경로 사용
                export_dir = r"C:\Users\elaus\Projects\Eclass\export"
                print(f"절대 경로 사용: {export_dir}")

            # export 디렉토리가 없으면 생성
            os.makedirs(export_dir, exist_ok=True)
            print(f"내보내기 디렉토리 생성 완료")
            
            # 파일 이름에 사용할 수 없는 문자 제거
            safe_course_id = ''.join(c for c in course_id if c.isalnum() or c in ('-', '_'))
            filename = os.path.join(export_dir, f"강의계획서_{safe_course_id}.txt")
            print(f"저장할 파일 경로: {filename}")
            
            # 파일 쓰기
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text_content)
            
            print(f"강의계획서가 '{filename}' 파일로 저장되었습니다.")
            return True
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {str(e)}")
            print(f"현재 작업 디렉토리: {os.getcwd()}")
            return False

    def _print_plan_info(self, plan_info: Dict[str, Any]):
        print("\n=== 강의계획서 정보 ===")
        for section, content in plan_info.items():
            print(f"\n{section}:")
            if isinstance(content, dict):
                for key, value in content.items():
                    print(f"  {key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    print(f"  {item['주차']}. {item['내용']}")
                    if item['비고']:
                        print(f"     비고: {item['비고']}")
