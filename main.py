from scrapping.eclass_manager import EclassManager
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    manager = EclassManager()
    await manager.run()

if __name__ == "__main__":
    asyncio.run(main())