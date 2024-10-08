import os
from playwright.async_api import async_playwright
from urllib.parse import urlencode
from datetime import datetime
from scrapping.eclass_session import EclassSession
from .html_parser import HTMLParser
from config import BASE_URL
import logging
import json
from typing import Dict, List, Optional, Callable
from bs4 import BeautifulSoup

class PlaywrightScraper:
    def __init__(self):
        self.eclass_session = EclassSession()
        self.parser = HTMLParser()

    async def _setup_browser(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        return browser, page

    async def _handle_popups(self, page):
        for popup in page.context.pages:
            if popup != page:
                await popup.close()

    async def _login(self, page, login_url):
        await page.goto(login_url)
        await self._handle_alert(page)

        try:
            await page.fill("#usr_id", self.eclass_session.username)
            await page.fill("#usr_pwd", self.eclass_session.password)
            await page.click("input[type='image'][alt='확인']")
        except Exception as e:
            raise

    async def _handle_alert(self, page):
        try:
            alert = await page.wait_for_event("dialog", timeout=3000)
            await alert.accept()
        except:
            pass

    async def get_page(self, page, url):
        try:
            await page.goto(url)
            return await page.content()
        except Exception as e:
            return None

    async def scrape(self, params, parsed_params, list_view_url):
        session_info = self.eclass_session.get_detailed_session_info()

        ky_code = params.get('ky', '')
        if not ky_code:
            raise ValueError("KY code is missing or empty. Cannot enter the classroom.")

        try:
            browser, page = await self._setup_browser()
            await self._login(page, session_info['login_url'])

            ajax_script = f"""
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/ilos/st/course/eclass_room2.acl', false);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('KJKEY={ky_code}&returnData=json&returnURI=/ilos/st/course/submain_form.acl&encoding=utf-8');
            return xhr.responseText;
            """

            response_text = await page.evaluate(ajax_script)
            response_data = json.loads(response_text)
            if response_data.get('isError'):
                raise Exception(response_data.get('message'))

            return_url = response_data.get('returnURL')
            if not return_url:
                raise Exception("No return URL provided in the response")

            ordered_params = [
                ('ARTL_NUM', parsed_params.get('ARTL_NUM', '')),
                ('SCH_KEY', params.get('SCH_KEY', '')),
                ('SCH_VALUE', params.get('SCH_VALUE', '')),
                ('display', params.get('display', '1')),
                ('start', params.get('start', '1'))
            ]
            encoded_params = '&'.join(f"{k}={urlencode({k: str(v)}).split('=')[1]}" for k, v in ordered_params)
            lecture_material_url = f"{list_view_url}?{encoded_params}"

            page_source = await self.get_page(page, lecture_material_url)
            return page_source
        except Exception as e:
            return None
        finally:
            await browser.close()

    async def save_debug_html(self, html_content, base_filename):
        debug_dir = 'debug'
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.html"
        filepath = os.path.join(debug_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("<!-- This file is created for debugging purposes. -->\n")
            f.write(html_content)

    async def fetch_and_parse_list(self, url: str, params: Dict[str, str], save_filename: str) -> Optional[Dict[str, List]]:
        async with async_playwright() as p:
            browser, page = await self._setup_browser()
            response = await self.get_page(page, url)
            await self.save_debug_html(response, save_filename)
            
            if response:
                items_data = await self.parser.parse_list(response)
                items = items_data['items']
                parsed_data = items_data['ARTL_NUMs']
                return items, parsed_data
            else:
                logging.error(f"Error fetching list from {url}")
                return None

    async def attachments_list(self, params, parsed_params: Dict[str, List]) -> List[Dict[str, str]]:
        list_view_url = f"{BASE_URL}/ilos/st/course/lecture_material_view_form.acl"
        all_attachments = []

        for artl_num in parsed_params.get('ARTL_NUMs', []):
            current_params = parsed_params.copy()
            current_params['ARTL_NUM'] = artl_num

            # 동적으로 생성된 첨부파일 페이지 가져오기
            page_content = await self.scrape(params, current_params, list_view_url)
            await self.save_debug_html(page_content, f"dynamic_generated_page_{artl_num}")

            # 파싱 함수 호출
            attachments = self.parser.parse_attachments(page_content)
            all_attachments.extend(attachments)

        return all_attachments

    async def display_list_and_navigate(self, 
                                        items: List[Dict[str, str]],
                                        get_content: Callable[[str], str],
                                        clean_content: Callable[[BeautifulSoup], str],
                                        parsed_params: Dict[str, List],
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
                    await self.display_detail_page(
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

    async def display_detail_page(self, item: Dict[str, str],
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
            await self.save_debug_html(content, 'test_for_file.html')
        
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
            await self.display_attachments(params, parsed_params)
        else:
            print("조회할 첨부파일이 없습니다.")
        
        input("\n엔터를 누르면 목록으로 돌아갑니다...")

    async def display_attachments(self, params, parsed_params: Dict[str, List]) -> None:
        files = await self.attachments_list(params, parsed_params)
        
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
                    print(f"{selected_file['name']} 다운로드 완료.")
                    break
                else:
                    print("올바른 번호를 입력해주세요.")
            except ValueError:
                print("숫자를 입력해주세요.")