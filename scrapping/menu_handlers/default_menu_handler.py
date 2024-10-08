from .base import MenuHandler
from typing import Dict
import logging

class DefaultMenuHandler(MenuHandler):
    def __init__(self, session, course_id):
        super().__init__(session, course_id)
        self.logger = logging.getLogger(__name__)

    async def handle(self, menu_data: Dict[str, str]) -> None:
        self.logger.warning(f"DefaultMenuHandler invoked for course_id: {self.course_id}. No specific handler found for the menu.")
        print(f"해당 메뉴에 대한 핸들러가 존재하지 않습니다. Course ID: {self.course_id}")