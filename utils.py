import os

def save_html_content(html_content: str, filename: str, debug_dir: str = None) -> None:
    try:
        if not debug_dir:
            debug_dir = os.path.join(os.getcwd(), 'debug')
        os.makedirs(debug_dir, exist_ok=True)

        file_path = os.path.join(debug_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML 내용이 {file_path}에 저장되었습니다.")
    except Exception as e:
        print(f"HTML 내용 저장 중 오류가 발생했습니다: {e}")