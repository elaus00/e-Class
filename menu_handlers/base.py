from abc import ABC, abstractmethod
from typing import Dict
from eclass_session import EclassSession

class MenuHandler(ABC):
    def __init__(self, session: EclassSession, course_id: str):
        self.session = session
        self.course_id = course_id

    @abstractmethod
    def handle(self, menu_data):
        pass