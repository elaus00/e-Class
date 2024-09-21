import re
from bs4 import BeautifulSoup
from typing import Dict, List
from config import BASE_URL
import logging

class HTMLParser:
    ROW_STYLE = "cursor: pointer;"
    BASE_URL = BASE_URL

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_list(self, html_content: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        item_rows = soup.find_all('tr', style=self.ROW_STYLE)
        
        if not item_rows:
            self.logger.warning("Could not find any rows with style 'cursor: pointer;'")
            return []

        items = [self._parse_row(row) for row in item_rows if len(row.find_all('td')) >= 5]
        items.reverse()

        return items

    def _parse_row(self, row) -> Dict[str, str]:
        cols = row.find_all('td')
        title_element = cols[2].find('a', class_='site-link')
        
        title, author, views = self._parse_title_element(title_element)
        onclick_value = cols[2].get('onclick', '')
        detail_url = self._extract_detail_url(onclick_value)
        
        item = {
            'number': cols[0].text.strip(),
            'title': title,
            'author': author,
            'date': cols[4].text.strip(),
            'views': views,
            'detail_url': detail_url
        }
        return item

    def _parse_title_element(self, title_element):
        if not title_element:
            return '', '', ''
        
        title = title_element.find('div', class_='subjt_top').text.strip()
        subjt_bottom = title_element.find('div', class_='subjt_bottom')
        author = subjt_bottom.find('span').text.strip()
        views = subjt_bottom.find_all('span')[-1].text.strip().split()[-1]
        
        return title, author, views

    def _extract_detail_url(self, onclick_value: str) -> str:
        url_pattern = r"pageMove\('([^']+)'"
        match = re.search(url_pattern, onclick_value)
        if match:
            relative_url = match.group(1)
            relative_url = relative_url.split('&')[0]
            return self.BASE_URL + relative_url
        else:
            self.logger.warning(f"Could not extract URL from onclick value: {onclick_value}")
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
            'attachments': self._parse_attachments(textviewer)
        }

    def _parse_attachments(self, textviewer: BeautifulSoup) -> List[Dict[str, str]]:
        file_div = textviewer.find('div', id='tbody_file')
        if not file_div:
            return []

        attachments = []
        for file in file_div.find_all('a', class_='site-link'):
            attachments.append({
                'name': file.text.strip(),
                'url': self.BASE_URL + file['href']
            })
        
        return attachments

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