import os
import logging
import requests
from urllib.parse import unquote
from tqdm import tqdm
from typing import Optional

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
def download_file(url: str, filename: str, session=None) -> None:
    """
    주어진 URL에서 파일을 다운로드하고 지정된 파일 이름으로 저장합니다.
    다운로드 진행 상황을 프로그레스 바로 표시합니다.

    :param url: 다운로드할 파일의 URL
    :param filename: 저장할 파일 이름
    :param session: 기존 requests.Session 객체 (선택사항)
    """
    try:
        if session is None:
            session = requests.Session()

        # User-Agent 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # 첫 번째 요청으로 리다이렉션 및 실제 다운로드 URL 확인
        response = session.get(url, headers=headers, allow_redirects=True, stream=True)
        response.raise_for_status()

        # 실제 다운로드 URL 및 파일 이름 확인
        actual_url = response.url
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            filename = unquote(content_disposition.split('filename=')[-1].strip('"'))

        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192  # 8 KB

        # 파일 다운로드
        with open(filename, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                progress_bar.update(size)

        # 다운로드 완료 후 파일 크기 확인
        if os.path.getsize(filename) < total_size:
            raise IOError("다운로드된 파일의 크기가 예상보다 작습니다.")

        print(f"\n'{filename}' 다운로드가 완료되었습니다.")

    except requests.RequestException as e:
        print(f"다운로드 중 오류가 발생했습니다: {e}")
    except IOError as e:
        print(f"파일을 저장하는 중 오류가 발생했습니다: {e}")
        if os.path.exists(filename):
            os.remove(filename)  # 불완전한 파일 제거