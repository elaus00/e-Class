from . import MenuHandler
from typing import Dict, List, Optional

class DefaultMenuHandler(MenuHandler):
    def handle(self, menu_data: Dict[str, str]) -> None:
        print(f"메뉴 '{menu_data['name']}'에 대한 처리가 구현되지 않았습니다.")
