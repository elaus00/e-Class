import os
import logging
import requests
from typing import Optional, Dict, List
from config import BASE_URL
from urllib.parse import urljoin
from utils.dynamic_page import SeleniumScraper

logger = logging.getLogger(__name__)

# html 파일 저장
def save_html_content(html_content: str, filename: str, debug_dir: Optional[str] = None, logger: logging.Logger = logger) -> None:
    try:
        if not debug_dir:
            debug_dir = os.path.join(os.getcwd(), 'debug')
        os.makedirs(debug_dir, exist_ok=True)

        file_path = os.path.join(debug_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML 내용이 {file_path}에 저장되었습니다.")
    except Exception as e:
        logger.error(f"HTML 내용 저장 중 오류가 발생했습니다: {e}")

# 첨부파일 다운로드
def download_file(file: Dict[str, str]) -> None:
    download_url = urljoin(BASE_URL, '/ilos/co/efile_download.acl')
    
    try:
        response = requests.get(download_url, params=file['params'], stream=True)
        response.raise_for_status()
        
        # 다운로드 디렉토리 생성
        download_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        file_path = os.path.join(download_dir, file['name'])
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"파일 '{file['name']}'을(를) 성공적으로 다운로드했습니다.")
        
    except requests.RequestException as e:
        print(f"파일 다운로드 중 오류가 발생했습니다: {e}")
    except IOError as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

