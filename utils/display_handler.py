from typing import List, Dict, Callable
from bs4 import BeautifulSoup
import os
import re
from .file_handler import fetch_file_list, download_file, save_html_content
from config import BASE_URL

def display_detail_page(item: Dict[str, str], 
                        get_content: Callable[[str], str], 
                        clean_content: Callable[[BeautifulSoup], str],
                        base_url: str):
    item_url = item['detail_url']
    content = get_content(item_url)
    
    if not content:
        print(f"{item['title']} 페이지를 불러올 수 없습니다.")
        return

    soup = BeautifulSoup(content, 'html.parser')
    
    # 디버깅용 코드
    save_html_content(content, 'test_for_file.html')
    
    textviewer = soup.find('td', class_='textviewer')
    
    if not textviewer:
        print(f"{item['title']} 페이지를 파싱할 수 없습니다.")
        return

    print(f"\n=== {item['title']} ===")
    print(f"작성자: {item['author']}")
    print(f"게시일: {item['date']}")
    print(f"조회수: {item['views']}")
    print("\n내용:")
    
    content_paragraphs = textviewer.find_all('p')
    if content_paragraphs:
        for p in content_paragraphs:
            cleaned_content = clean_content(p)
            print(cleaned_content)
    else:
        print("내용을 찾을 수 없습니다.")

    print("\n첨부파일:")
    
    content_seq_script = soup.find('script', text=re.compile(r'CONTENT_SEQ\s*:\s*"(\w+)"'))
    if content_seq_script:
        content_seq = re.search(r'CONTENT_SEQ\s*:\s*"(\w+)"', content_seq_script.string).group(1)
        file_list_html = fetch_file_list(item_url, content_seq)
        if file_list_html:
            display_attachments(file_list_html, base_url, download_file)
        else:
            print("첨부 파일을 가져올 수 없습니다.")
    else:
        print("첨부 파일 정보를 찾을 수 없습니다.")

    input("\n엔터를 누르면 목록으로 돌아갑니다...")

def display_list_and_navigate(items: List[Dict[str, str]], 
                              get_content: Callable[[str], str],
                              clean_content: Callable[[BeautifulSoup], str],
                              title: str = "목록",
                              item_type: str = "항목") -> None:
    print(f"\n=== {title} ===")
    print("=" * 30)
    for item in items:
        print(f"{item['number']:>3}. {item['title']:<30} | {item['author']:<10} | 조회수: {item['views']:<5} | {item['date']}")
    print("=" * 30)
    
    while True:
        choice = input(f"\n상세히 볼 {item_type} 번호를 입력하세요 (0: 돌아가기): ")
        if choice == '0':
            break
        try:
            choice = int(choice)
            if 1 <= choice <= len(items):
                display_detail_page(
                    items[choice-1],
                    get_content=get_content,
                    clean_content=clean_content,
                    base_url=BASE_URL,
                )
                break
            else:
                print("올바른 번호를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
            
def display_attachments(file_list_html: str, download_file: Callable[[str, str, str], None]) -> None:
    soup = BeautifulSoup(file_list_html, 'html.parser')
    file_links = soup.find_all('a', class_='site-link')
    
    if file_links:
        for idx, file in enumerate(file_links, 1):
            print(f"{idx}. {file.text.strip()}")
        
        while True:
            choice = input("\n다운로드할 파일 번호를 입력하세요 (0: 취소): ")
            if choice == '0':
                break
            try:
                choice = int(choice)
                if 1 <= choice <= len(file_links):
                    file = file_links[choice - 1]
                    file_url = BASE_URL + file['href']
                    filename = file.text.strip()
                    download_dir = os.path.join(os.getcwd(), 'downloads')
                    download_file(file_url, filename, download_dir)
                    break
                else:
                    print("올바른 번호를 입력해주세요.")
            except ValueError:
                print("숫자를 입력해주세요.")
    else:
        print("첨부 파일이 없습니다.")