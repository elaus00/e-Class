from typing import Dict, List, Optional
from scrapping.eclass_session import EclassSession
from .file_handler import save_html_content
from .html_parser import HTMLParser
from .dynamic_page import SeleniumScraper
from config import BASE_URL

import logging
        
parser = HTMLParser()

def fetch_and_parse_list(url: str, 
                         params: Dict[str, str],
                         session: EclassSession,
                         save_filename: str) -> Optional[Dict[str, List]]:
    
    response = session.post_request(url, params)
    
    # 테스트용 코드 (강의자료 디버깅 + 시간)
    save_html_content(response, save_filename)    
    
    if response:
        parser = HTMLParser()
        items, parsed_data = parser.parse_list(response)
        return items, parsed_data
    else:
        logging.error(f"Error fetching list from {url}")
        return None
        
# 첨부파일 리스팅
def attachments_list(params, parsed_params: Dict[str, List]) -> List[Dict[str, str]]:
    selenium_scraper = SeleniumScraper()
    list_view_url = f"{BASE_URL}/ilos/st/course/lecture_material_view_form.acl"
    all_attachments = []

    for artl_num in parsed_params.get('ARTL_NUMs', []):
        current_params = parsed_params.copy()
        current_params['ARTL_NUM'] = artl_num
        
        # 동적으로 생성된 첨부파일 페이지 가져오기
        page_content = selenium_scraper.scrape(params, current_params, list_view_url)
        selenium_scraper.save_debug_html(page_content, f"dynamic_generated_page_{artl_num}")

        # 파싱 함수 호출
        attachments = parser.parse_attachments(page_content)
        all_attachments.extend(attachments)

    return all_attachments
        