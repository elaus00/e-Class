from bs4 import BeautifulSoup
from config import BASE_URL
from scrapping.eclass_session import EclassSession
from utils import save_html_content

class LectureMaterialMenuHandler:
    def __init__(self, session : EclassSession, course_id):
        self.session = session
        self.course_id = course_id
        self.username = session.username

    def get_lecture_material_list(self, start=1, search_value=''):
        list_url = f"{BASE_URL}/ilos/st/course/lecture_material_list.acl"
        params = {
            'start': str(start),
            'display': '1',
            'SCH_VALUE': search_value,
            'ud': self.username,
            'ky': self.course_id,
            'encoding': 'utf-8'
        }
        response = self.session.post_request(list_url, params)
        save_html_content(response, "강의자료 리스트.html")
        
        if response:
            material_list = self.parse_lecture_material_list(response)
            self.display_lecture_material_list(material_list)
        else:
            print("Error fetching lecture material list")
            return None

    def parse_lecture_material_list(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        material_rows = soup.select('table.bbslist > tbody > tr')

        materials = []
        for row in material_rows:
            columns = row.select('td')
            if len(columns) >= 5:
                title_column = columns[2].select_one('a.site-link')
                if title_column:
                    title = title_column.select_one('div.subjt_top').text.strip()
                    date_and_views = title_column.select_one('div.subjt_bottom').text.strip().split()
                    author = date_and_views[0]
                    views = date_and_views[-1].replace('조회', '').strip()
                    date = columns[4].text.strip()

                    material = {
                        'number': columns[0].text.strip(),
                        'title': title,
                        'author': author,
                        'views': views,
                        'date': date,
                        'link': self.extract_material_link(row)
                    }
                    materials.append(material)

        return materials
            
    def extract_material_link(self, row):
        link_element = row.select_one('a')
        if link_element:
            href = link_element.get('href')
            return f"{BASE_URL}{href}"
        return None

    def display_lecture_material_list(self, materials):
        print("강의 자료 목록:")
        print("=" * 30)
        for material in materials:
            print(f"{material['number']:>3}. {material['title']:<30} | {material['author']:<10} | 조회수: {material['views']:<5} | {material['date']}")
        print("=" * 30)

    def handle(self, menu_data):
        html_content = self.get_lecture_material_list()
        if html_content:
            materials = self.parse_lecture_material_list(html_content)
            return materials
        else:
            return []