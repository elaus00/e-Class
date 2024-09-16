from eclass_session import EclassSession, Course, MenuType
from menu_handlers.factory import MenuFactory
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    eclass = EclassSession()
    if eclass.login():
        courses = eclass.get_course_list()
        print("수강 중인 과목:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course.name} (코드: {course.code}, 시간: {course.time}, ID: {course.id})")
      
        while True:
            try:
                choice = int(input("\n정보를 확인할 과목 번호를 입력하세요 (0 입력시 종료): ")) - 1
                if choice == -1:
                    print("프로그램을 종료합니다.")
                    break
                selected_course = courses[choice]
            except (ValueError, IndexError):
                logging.error("잘못된 입력입니다. 다시 시도해주세요.")
                continue

            course_menus = eclass.get_course_menus(selected_course.id)
            
            if not course_menus:
                print("메뉴를 가져오는 데 실패했습니다.")
                continue

            while True:
                print(f"\n{selected_course.name} 과목 메뉴:")
                for i, (menu_type, menu_data) in enumerate(course_menus.items(), 1):
                    print(f"{i}. {menu_data['name']} (유형: {menu_type.name})")
                
                try:
                    menu_choice = int(input("\n접속할 메뉴 번호를 입력하세요 (0 입력시 과목 선택으로 돌아가기): ")) - 1
                    if menu_choice == -1:
                        break
                    menu_type, menu_data = list(course_menus.items())[menu_choice]
                except (ValueError, IndexError):
                    logging.error("잘못된 입력입니다. 다시 시도해주세요.")
                    continue

                handler = MenuFactory.create_handler(menu_type, eclass)
                handler.handle(menu_data)
                
                input("\n엔터를 눌러 계속...")

if __name__ == "__main__":
    main()