import os
from bs4 import BeautifulSoup
from .base import MenuHandler
from typing import Dict, List
from config import BASE_URL, get_config
from scrapping.eclass_session import EclassSession
import re

class NoticeMenuHandler(MenuHandler):
    def __init__(self, session: EclassSession, course_id: str):
        super().__init__(session, course_id)
        self.config = get_config()

    def handle(self, menu_data: Dict[str, str] = None) -> None:
        self._handle_notices()

    def _handle_notices(self) -> None:
        notice_url = f"{BASE_URL}/ilos/st/course/notice_list.acl"
        data = {
            'start': '1',
            'display': '1',
            'SCH_VALUE': '',
            'ud': self.config['credentials']['username'],
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        
        # logging.info(f"Sending request to {notice_url}")
        content = self.session.post_request(notice_url, data)
        # logging.info(f"Received response. Content length: {len(content)}")
        
        if content:
            notices = self._parse_notices(content)
            self._display_notices(notices)
        else:
            # logging.error("No content received from the server")
            print("공지사항을 불러올 수 없습니다.")

    def _parse_notices(self, html_content: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        notice_rows = soup.find_all('tr', style="cursor: pointer;")
        
        if not notice_rows:
            # logging.warning("Could not find any rows with style 'cursor: pointer;'")
            return []

        notices = []
        for row in notice_rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                title_element = cols[2].find('a', class_='site-link')
                title = title_element.find('div', class_='subjt_top').text.strip() if title_element else ''
                author = title_element.find('div', class_='subjt_bottom').find('span').text.strip() if title_element else ''
                views = title_element.find('div', class_='subjt_bottom').find_all('span')[-1].text.strip().split()[-1] if title_element else ''
                onclick_value = cols[2].get('onclick', '')
                detail_url = self._extract_detail_url(onclick_value)
                
                notice = {
                    'number': cols[0].text.strip(),
                    'title': title,
                    'author': author,
                    'date': cols[4].text.strip(),
                    'views': views,
                    'detail_url': detail_url
                }
                notices.append(notice)
                # logging.info(f"Parsed notice: {notice}")
        notices.reverse()

        return notices

    def _extract_detail_url(self, onclick_value: str) -> str:
        match = re.search(r"pageMove\('([^']+)'\)", onclick_value)
        if match:
            return BASE_URL + match.group(1)
        return ""

    def _display_notices(self, notices: List[Dict[str, str]]) -> None:
        print("\n=== 공지사항 목록 ===")
        for idx, notice in enumerate(notices, 1):
            print(f"{idx}. 제목: {notice['title']}")
            print(f"   작성자: {notice['author']}")
            print(f"   게시일: {notice['date']}")
            print(f"   조회수: {notice['views']}")
            print("-" * 30)
        
        while True:
            choice = input("\n상세히 볼 공지사항 번호를 입력하세요 (0: 돌아가기): ")
            if choice == '0':
                break
            try:
                choice = int(choice)
                if 1 <= choice <= len(notices):
                    self._display_notice_detail(notices[choice-1])
                    break
                else:
                    print("올바른 번호를 입력해주세요.")
            except ValueError:
                print("숫자를 입력해주세요.")

    # 공지사항 세부 정보 확인
    def _display_notice_detail(self, notice: Dict[str, str]) -> None:
        detail_url = notice['detail_url']
        if not detail_url:
            print("공지사항 상세 정보를 불러올 수 없습니다.")
            return

        content = self.session.post_request(detail_url, data={})
        if not content:
            print("공지사항 상세 내용을 불러올 수 없습니다.")
            return

        soup = BeautifulSoup(content, 'html.parser')
        textviewer = soup.find('td', class_='textviewer')
        
        if not textviewer:
            print("공지사항 상세 내용을 파싱할 수 없습니다.")
            return

        print("\n=== 공지사항 상세 ===")
        print(f"제목: {notice['title']}")
        print(f"작성자: {notice['author']}")
        print(f"게시일: {notice['date']}")
        print(f"조회수: {notice['views']}")
        print("\n내용:")
        
        content_div = textviewer.find('div')
        if content_div:
            # HTML 태그 처리
            for br in content_div.find_all('br'):
                br.replace_with('\n')
            
            for p in content_div.find_all('p'):
                p.insert_after(soup.new_string('\n'))
            
            # 공백 유지하면서 텍스트 추출
            cleaned_content = ''
            for element in content_div.contents:
                if element.name == 'p':
                    cleaned_content += element.get_text(strip=False) + '\n'
                elif isinstance(element, str):
                    cleaned_content += element
            
            # 연속된 빈 줄 제거
            cleaned_content = '\n'.join([line for line in cleaned_content.splitlines() if line.strip() or line.isspace()])
            
            # 줄 바꿈 유지하면서 출력
            print(cleaned_content)
        else:
            print("내용을 찾을 수 없습니다.")
        
        # 첨부 파일 처리
        file_div = textviewer.find('div', id='tbody_file')
        if file_div and file_div.contents:
            print("\n첨부 파일:")
            for file in file_div.find_all('a'):
                print(f"- {file.text.strip()}")
        
        input("\n엔터를 누르면 목록으로 돌아갑니다...")