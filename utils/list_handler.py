from typing import List, Dict, Optional, Callable, Any
from .file_handler import save_html_content
from .html_parser import HTMLParser
import logging

def fetch_and_parse_list(url: str, 
                         params: Dict[str, str], 
                         post_request: Callable[[str, Dict[str, str]], str],
                         display_list: Callable[[List[Dict[str, str]]], None],
                         save_filename: str,
                         instance: Any = None) -> Optional[List[Dict[str, str]]]:
    response = post_request(url, params)
    
    # 테스트용 코드
    save_html_content(response, save_filename)    
    
    parser = HTMLParser()

    if response:
        item_list = parser.parse_list(response)
        if display_list:
            display_list(item_list)
        return item_list
    else:
        logging.logger.error(f"Error fetching list from {url}")
        return None