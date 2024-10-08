from typing import Dict, Type
from scrapping.eclass_session import EclassSession, MenuType
from .base import MenuHandler
from . import (
    PlanMenuHandler,
    OnlineLectureMenuHandler,
    NoticeMenuHandler,
    LectureMaterialMenuHandler,
    AttendanceMenuHandler,
    AssignmentMenuHandler,
    TeamProjectMenuHandler,
    ExamMenuHandler,
    DefaultMenuHandler,
)
import asyncio

class MenuFactory:
    handler_map: Dict[MenuType, Type[MenuHandler]] = {
        MenuType.PLAN: PlanMenuHandler,
        MenuType.ONLINE_LECTURE: OnlineLectureMenuHandler,
        MenuType.NOTICE: NoticeMenuHandler,
        MenuType.LECTURE_MATERIAL: LectureMaterialMenuHandler,
        MenuType.ATTENDANCE: AttendanceMenuHandler,
        MenuType.ASSIGNMENT: AssignmentMenuHandler,
        MenuType.TEAM_PROJECT: TeamProjectMenuHandler,
        MenuType.EXAM: ExamMenuHandler,
        
    }

    @classmethod
    async def create_handler(cls, menu_type: MenuType, session: EclassSession, course_id: str) -> MenuHandler:
        handler_class = cls.handler_map.get(menu_type, DefaultMenuHandler)
        return handler_class(session, course_id)

    @classmethod
    async def create_handler_async(cls, menu_type: MenuType, session: EclassSession, course_id: str) -> MenuHandler:
        handler_class = cls.handler_map.get(menu_type, DefaultMenuHandler)
        return await asyncio.to_thread(handler_class, session, course_id)
