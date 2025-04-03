from selenium import webdriver

from src.modules.loader.notion_loader import NotionLoader

if __name__ == "__main__":
    notion_url = "https://sincere-nova-ec6.notion.site/a8bbcb69d87c4c19aabee16c6a178286"
    loader = NotionLoader(webdriver.Chrome())
    document = loader.load(notion_url)

    if document is not None:
        print(document)
        print("\n크롤링 완료!")
