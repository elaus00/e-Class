import os
import configparser
from openai import OpenAI
import json

# 설정 파일 읽기
config = configparser.ConfigParser()
config.read('config.ini')

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=config['api']['key'])

# 텍스트 파일 읽기 함수
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# ChatGPT를 사용한 텍스트 요약 함수
def summarize_text(text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # 또는 사용 가능한 다른 모델
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"한글로 텍스트를 요약해봐:\n\n{text}"}
        ]
    )
    return completion.choices[0].message.content

# 결과 저장 함수
def save_result(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

# 메인 처리 함수
def process_text_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_path = os.path.join(current_dir, '..', 'scrapping', 'export')

    input_dir = export_path  # 입력 파일이 있는 디렉토리 경로
    output_file = 'summaries.json'  # 결과를 저장할 파일 이름
    summaries = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(input_dir, file_name)
            text = read_text_file(file_path)
            
            print(f"Summarizing {file_name}...")
            summary = summarize_text(text)
            
            summaries.append({
                "file_name": file_name,
                "summary": summary
            })
    
    save_result(output_file, summaries)
    print(f"Summaries saved to {output_file}")

# JSON을 마크다운으로 변환하는 함수
def json_to_markdown(json_file_path, markdown_file_path):
    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        summaries = json.load(json_file)
    
    # 마크다운 내용 생성
    markdown_content = "# 텍스트 파일 요약\n\n"
    
    for item in summaries:
        file_name = item['file_name']
        summary = item['summary']
        
        markdown_content += f"## {file_name}\n\n"
        markdown_content += f"{summary}\n\n"
        markdown_content += "---\n\n"  # 각 요약 사이에 구분선 추가
    
    # 마크다운 파일 저장
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)

    print(f"마크다운 파일이 생성되었습니다: {markdown_file_path}")

# 실행
if __name__ == "__main__":
    process_text_files()
    
    # JSON을 마크다운으로 변환
    json_file = 'summaries.json'
    markdown_file = 'summaries.md'
    json_to_markdown(json_file, markdown_file)