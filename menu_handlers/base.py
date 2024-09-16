from abc import ABC, abstractmethod
from typing import Dict
from eclass_session import EclassSession

class MenuHandler(ABC):
    def __init__(self, session: EclassSession):
        self.session = session

    @abstractmethod
    def handle(self, menu_data: Dict[str, str]) -> None:
        pass