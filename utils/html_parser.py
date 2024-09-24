import re
from bs4 import BeautifulSoup
from typing import Dict, List
from config import BASE_URL
import logging

class HTMLParser:
    ROW_STYLE = "cursor: pointer;"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_list(self, html_content: str) -> Dict[str, List]:
        soup = BeautifulSoup(html_content, 'html.parser')
        item_rows = soup.find_all('tr', style=self.ROW_STYLE)
        
        if not item_rows:
            self.logger.warning("Could not find any rows with style 'cursor: pointer;'")
            return {'items': [], 'ARTL_NUMs': []}

        items = [self._parse_row(row) for row in item_rows if len(row.find_all('td')) >= 5]
        items.reverse()

        # 모든 ARTL_NUM을 별도의 리스트로 추출
        all_artl_nums = [item['ARTL_NUM'] for item in items if item['ARTL_NUM']]

        return items, {'items': items, 'ARTL_NUMs': all_artl_nums}

    def _parse_row(self, row) -> Dict[str, str]:
        cols = row.find_all('td')
        title_element = cols[2].find('a', class_='site-link')
        
        title, author, views = self._parse_title_element(title_element)
        onclick_value = cols[2].get('onclick', '')
        detail_url = self._extract_detail_url(onclick_value)
        # ARTL_NUM 추출
        artl_num = self._extract_artl_num(onclick_value)
        
        # CONTENT_SEQ 추출
        content_seq = self._extract_content_seq(cols[3])
        
        item = {
            'number': cols[0].text.strip(),
            'title': title,
            'author': author,
            'date': cols[4].text.strip(),
            'views': views,
            'detail_url': detail_url,
            'ARTL_NUM': artl_num,
            'CONTENT_SEQ': content_seq
        }
        return item

    def _parse_title_element(self, title_element):
        if not title_element:
            return '', '', ''  # title_element가 None인 경우 빈 문자열 반환

        # 'subjt_top' 클래스를 가진 div를 찾고, 없으면 'a' 태그 내의 첫 번째 div를 사용
        subjt_top = title_element.find('div', class_='subjt_top')
        if subjt_top:
            title = subjt_top.text.strip()
        else:
            title = title_element.find('div').text.strip() if title_element.find('div') else ''  # 기본 div에서 제목 추출

        subjt_bottom = title_element.find('div', class_='subjt_bottom')
        author = subjt_bottom.find('span').text.strip() if subjt_bottom and subjt_bottom.find('span') else ''
        views = subjt_bottom.find_all('span')[-1].text.strip().split()[-1] if subjt_bottom and len(subjt_bottom.find_all('span')) > 0 else ''

        return title, author, views

    def _extract_detail_url(self, onclick_value: str) -> str:
        url_pattern = r"pageMove\('([^']+)'"
        match = re.search(url_pattern, onclick_value)
        if match:
            relative_url = match.group(1)
            relative_url = relative_url.split('&')[0]
            return BASE_URL + relative_url
        else:
            self.logger.warning(f"Could not extract URL from onclick value: {onclick_value}")
            return ""

    def _extract_artl_num(self, onclick_value: str) -> str:
        artl_num_pattern = r"ARTL_NUM=(\d+)"
        match = re.search(artl_num_pattern, onclick_value)
        if match:
            return match.group(1)
        else:
            self.logger.warning(f"Could not extract ARTL_NUM from onclick value: {onclick_value}")
            return ""

    def _extract_content_seq(self, attachment_col) -> str:
        download_icon = attachment_col.find('img', class_='download_icon')
        if download_icon and 'onclick' in download_icon.attrs:
            content_seq_pattern = r"downloadClick\('(.+?)'\)"
            match = re.search(content_seq_pattern, download_icon['onclick'])
            if match:
                return match.group(1)
        self.logger.warning("Could not extract CONTENT_SEQ from attachment column")
        return ""

    def parse_content(self, html_content: str) -> Dict[str, str]:
        soup = BeautifulSoup(html_content, 'html.parser')
        textviewer = soup.find('td', class_='textviewer')
        
        if not textviewer:
            self.logger.warning("Could not find content in textviewer class")
            return {}

        content = self.clean_content(textviewer)
        
        return {
            'content': content,
        }

    @staticmethod
    def clean_content(content_div: BeautifulSoup) -> str:
        for br in content_div.find_all('br'):
            br.replace_with('\n')
        
        for p in content_div.find_all('p'):
            p.insert_after(BeautifulSoup('\n', 'html.parser'))
        
        cleaned_content = ''
        for element in content_div.contents:
            if element.name == 'p':
                cleaned_content += element.get_text(strip=False) + '\n'
            elif isinstance(element, str):
                cleaned_content += element
        
        return '\n'.join([line for line in cleaned_content.splitlines() if line.strip() or line.isspace()])
    
    # 첨부파일 파싱
    def parse_attachments(self, html_content: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        attachments = []

        attfile_list = soup.find('div', class_='attfile-list')
        if attfile_list:
            file_links = attfile_list.find_all('a', class_='site-link')
            for link in file_links:
                file_url = link.get('href')
                file_title = link.text.strip()
                # 파일 크기 정보 추출
                size_match = re.search(r'\((.*?)\)$', file_title)
                file_size = size_match.group(1) if size_match else "Unknown size"
                # 파일 이름에서 크기 정보 제거
                file_name = re.sub(r'\s*\(.*?\)$', '', file_title).strip('- ')

                attachments.append({
                    'name': file_name,
                    'size': file_size,
                    'url': f"{BASE_URL}{file_url}" if file_url.startswith('/') else file_url
                })

        return attachments