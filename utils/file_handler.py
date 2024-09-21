import os
import logging
import requests
from typing import Optional, Callable

logger = logging.getLogger(__name__)

def save_html_content(html_content: str, filename: str, debug_dir: Optional[str] = None, logger: logging.Logger = logger) -> None:
    try:
        if not debug_dir:
            debug_dir = os.path.join(os.getcwd(), 'debug')  # 'DEBUG_DIR' 대신 직접 'debug' 사용
        os.makedirs(debug_dir, exist_ok=True)

        file_path = os.path.join(debug_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML 내용이 {file_path}에 저장되었습니다.")
    except Exception as e:
        logger.error(f"HTML 내용 저장 중 오류가 발생했습니다: {e}")


def download_file(url: str, filename: str, download_dir: str, logger: logging.Logger = logger) -> bool:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_path = os.path.join(download_dir, filename)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"{filename} 파일이 성공적으로 다운로드되었습니다.")
        return True
    except requests.RequestException as e:
        logger.error(f"파일 다운로드 중 오류가 발생했습니다: {e}")
        return False


def fetch_file_list(material_url: str, content_seq: str, extract_file_list_url: Callable[[str, str], Optional[str]], logger: logging.Logger = logger) -> Optional[str]:
    file_list_url = extract_file_list_url(material_url, content_seq)
    if file_list_url:
        try:
            response = requests.get(file_list_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"파일 목록을 가져오는 중 오류가 발생했습니다: {e}")
            return None
    else:
        return None