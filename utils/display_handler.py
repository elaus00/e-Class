from typing import List, Dict, Callable
from bs4 import BeautifulSoup
from .file_handler import save_html_content
from .list_handler import attachments_list

def display_list_and_navigate(items: List[Dict[str, str]], 
                              get_content: Callable[[str], str],
                              clean_content: Callable[[BeautifulSoup], str],
                              parsed_params : Dict[str, List],
                              params,
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
                    params=params,
                    parsed_params=parsed_params,
                )
                break
            else:
                print("올바른 번호를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
       
# 세부 페이지 보여주기            
def display_detail_page(item: Dict[str, str], 
                        get_content: Callable[[str], str], 
                        clean_content: Callable[[BeautifulSoup], str],
                        params,
                        parsed_params: Dict[str, List]):
    item_url = item['detail_url']
    content = get_content(item_url)
    
    if not content:
        print(f"{item['title']} 페이지를 불러올 수 없습니다.")
        return
    else:
        # 디버깅용 코드        
        save_html_content(content, 'test_for_file.html')
    
    soup = BeautifulSoup(content, 'html.parser')
    textviewer = soup.find('td', class_='textviewer')
    tbody_file = soup.find('div', id='tbody_file')
    
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

    # 첨부 파일이 존재하는 경우 처리
    if tbody_file:
        display_attachments(params, parsed_params)
    else:
        print("조회할 첨부파일이 없습니다.")
    
    input("\n엔터를 누르면 목록으로 돌아갑니다...")

# 강의자료 보여주기
def display_attachments(params, parsed_params: Dict[str, List]) -> None:
    files = attachments_list(params, parsed_params)
    
    if not files:
        print("첨부 파일이 없습니다.")
        return
    
    print("\n=== 첨부 파일 목록 ===")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file['name']} ({file['size']})")
    
    while True:
        choice = input("\n다운로드할 파일 번호를 입력하세요 (0: 취소): ")
        if choice == '0':
            break
        try:
            choice = int(choice)
            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]
                # download_file(selected_file['url'], selected_file['name'])
                print(f"{selected_file['name']} 다운로드 완료.")
                break
            else:
                print("올바른 번호를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
            