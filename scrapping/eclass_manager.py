from .eclass_session import EclassSession
from .menu_handlers.factory import MenuFactory
import logging
import asyncio

class EclassManager:
    def __init__(self):
        self.eclass = EclassSession()

    async def run(self):
        if not await self.eclass.login():
            logging.error("로그인 실패")
            return

        while True:
            courses = await self.eclass.get_course_list()
            self._display_courses(courses)
            selected_course = await self._select_course(courses)
            if selected_course is None:
                break

            await self._handle_course_menus(selected_course)

    def _display_courses(self, courses):
        print("\n수강 중인 과목:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course.name} (코드: {course.code}, 시간: {course.time}, ID: {course.id})")

    async def _select_course(self, courses):
        while True:
            try:
                choice = int(input("\n정보를 확인할 과목 번호를 입력하세요 (0 입력시 종료): ")) - 1
                if choice == -1:
                    return None
                return courses[choice]
            except (ValueError, IndexError):
                logging.error("잘못된 입력입니다. 다시 시도해주세요.")

    async def _handle_course_menus(self, course):
        course_menus = await self.eclass.get_course_menus(course.id)
        if not course_menus:
            print("메뉴를 가져오는 데 실패했습니다.")
            return

        while True:
            self._display_menus(course, course_menus)
            menu_type, menu_data = await self._select_menu(course_menus)
            if menu_type is None:
                break

            handler = await MenuFactory.create_handler_async(menu_type, self.eclass, course.id)
            await handler.handle(menu_data)
            
            input("\n엔터를 눌러 계속...")

    def _display_menus(self, course, course_menus):
        print(f"\n{course.name} 과목 메뉴:")
        for i, (menu_type, menu_data) in enumerate(course_menus.items(), 1):
            print(f"{i}. {menu_data['name']} (유형: {menu_type.name})")

    async def _select_menu(self, course_menus):
        while True:
            try:
                menu_choice = int(input("\n접속할 메뉴 번호를 입력하세요 (0 입력시 과목 선택으로 돌아가기): ")) - 1
                if menu_choice == -1:
                    return None, None
                return list(course_menus.items())[menu_choice]
            except (ValueError, IndexError):
                logging.error("잘못된 입력입니다. 다시 시도해주세요.")