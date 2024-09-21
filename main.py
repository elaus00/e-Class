from scrapping.eclass_manager import EclassManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    manager = EclassManager()
    manager.run()

if __name__ == "__main__":
    main()