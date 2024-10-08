from abc import ABC, abstractmethod
from scrapping.eclass_session import EclassSession

class MenuHandler(ABC):
    def __init__(self, session: EclassSession, course_id: str):
        self.session = session
        self.course_id = course_id

    @abstractmethod
    async def handle(self, menu_data):
        pass