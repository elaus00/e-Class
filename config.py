import configparser
import os

BASE_URL = "https://eclass.seoultech.ac.kr"
LOGIN_URL = f"{BASE_URL}/ilos/lo/login.acl"
MAIN_URL = f"{BASE_URL}/ilos/main/main_form.acl"
COURSE_ACCESS_URL = f"{BASE_URL}/ilos/st/course/eclass_room2.acl"
SUBMAIN_URL = f"{BASE_URL}/ilos/st/course/submain_form.acl"

def get_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_path)
    return config