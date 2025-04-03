import time
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NotionCrawler:
    def __init__(self, driver):
        self.driver = driver

    def read(self, url: str):
        """
            노션 페이지에서 notion-toggle-block 요소들을 찾아 클릭(펼치기) 후
            .docx 파일을 다운로드하는 예시.
            (파일 블록의 HTML 구조에 따라 XPath를 사용하며, 파일명에 포함된 공백은 '+'로 대체되고,
            동일한 기본 파일명이 이미 존재하면 다운로드를 스킵하며, 다운로드 후 파일명을 rename하고,
            페이지의 HTML을 읽어서 저장합니다.)
            """
        chrome_options = Options()
        # 자동 다운로드 설정: 다운로드 폴더를 ./files 로 지정
        prefs = {
            "download.default_directory": os.path.abspath("./files"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.add_argument("--headless")  # 필요에 따라 헤드리스 모드 사용

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(1)

        # 페이지의 모든 블록이 로드되도록 스크롤
        self.scroll_to_bottom()

        # (1) notion-toggle-block 요소 전체 찾기 및 클릭 (aria-expanded 상태 확인)
        toggle_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'notion-toggle-block')]")
        print(f"찾은 토글 블록 개수: {len(toggle_blocks)}")
        for toggle_block in toggle_blocks:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", toggle_block)
                toggle_button = toggle_block.find_element(By.XPATH, ".//div[@role='button']")
                aria_expanded = toggle_button.get_attribute("aria-expanded")
                if aria_expanded == "false":
                    WebDriverWait(driver, 10).until(
                        lambda d: toggle_button.is_displayed() and toggle_button.is_enabled())
                    toggle_button.click()
                else:
                    print("이미 열린 토글:", toggle_block.text)
            except Exception as e:
                print("토글 블록 클릭 실패:", e)

        self.scroll_to_bottom()

        # (2) .docx 파일 다운로드 처리 (새 탭에서 자동 다운로드 후 파일명 rename)
        self.download_docx_files()

        # HTML 읽기: 현재 페이지의 HTML 소스를 읽어서 ./files/page.html 에 저장
        page_html = driver.page_source
        html_file_path = os.path.join(os.path.abspath("./files"), "page.html")
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(page_html)
        print(f"HTML 파일 저장됨: {html_file_path}")

        driver.quit()
        return {}

    def scroll_to_bottom(self, pause_time=2):
        """
        페이지를 끝까지 스크롤하여 동적 로딩된 콘텐츠를 모두 표시하도록 유도.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def wait_for_download_and_rename(self, download_folder, target_file_name, timeout=30):
        """
        download_folder에서 .docx 파일이 다운로드 완료될 때까지 대기한 후,
        가장 최근의 다운로드된 .docx 파일을 target_file_name으로 rename합니다.
        """
        end_time = time.time() + timeout
        downloaded_file = None
        while time.time() < end_time:
            # .crdownload 확장자가 없고 .docx인 파일들 목록
            files = [f for f in os.listdir(download_folder) if f.endswith(".docx") and not f.endswith(".crdownload")]
            if files:
                # 가장 최근에 수정된 파일 선택
                downloaded_file = max(files, key=lambda f: os.path.getmtime(os.path.join(download_folder, f)))
                break
            time.sleep(1)
        if downloaded_file:
            original_path = os.path.join(download_folder, downloaded_file)
            target_path = os.path.join(download_folder, target_file_name)
            if original_path != target_path:
                os.rename(original_path, target_path)
                print(f"파일 이름 변경 완료: {downloaded_file} -> {target_file_name}")
        else:
            print("다운로드된 파일을 찾을 수 없습니다.")

    def download_docx_files(self, download_folder="./files"):
        """
        노션 페이지 내의 파일 블록 중 파일명이 .docx인 경우,
        해당 파일 블록을 클릭하면 새 탭에서 자동 다운로드가 진행되는 형태를 처리합니다.
        파일명에 포함된 공백은 '+'로 대체되며, 동일한 기본 파일명(숫자 접미사 무시)이 이미 존재하면 다운로드를 스킵합니다.
        다운로드 후, 다운로드된 파일명을 target_file_name으로 rename합니다.
        """
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        docx_files = []
        file_blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'notion-file-block')]")
        for block in file_blocks:
            try:
                # 파일 이름이 포함된 요소 찾기
                try:
                    file_name_element = block.find_element(By.XPATH, ".//*[contains(text(), '.docx')]")
                except Exception as e:
                    print("파일 이름 요소를 찾지 못했습니다:", e)
                    continue
                file_name = file_name_element.text.strip()
                # 공백을 '+'로 대체
                file_name = file_name.replace(" ", "+")
                download_path = os.path.abspath(download_folder)
                file_path = os.path.join(download_path, file_name)
                print(f"다운로드 파일 경로: {file_path}")
                # 기본 파일명 비교(숫자 접미사 제거)
                base_file_name = re.sub(r' \(\d+\)', '', file_name)
                existing_files = os.listdir(download_path)
                skip = False
                for existing in existing_files:
                    if existing.endswith('.docx'):
                        existing_base = re.sub(r' \(\d+\)', '', existing)
                        if existing_base == base_file_name:
                            skip = True
                            break
                if skip:
                    print(f"{file_name} 이미 존재하여 다운로드 스킵.")
                    continue

                if ".docx" in file_name:
                    print("다운로드 대상 파일:", file_name)
                    docx_files.append(file_name)
                    original_handle = self.driver.current_window_handle
                    block.click()
                    time.sleep(1)  # 새 탭이 열릴 시간 대기

                    handles = self.driver.window_handles
                    if len(handles) > 1:
                        for handle in handles:
                            if handle != original_handle:
                                try:
                                    self.driver.switch_to.window(handle)
                                    print("새 탭에서 자동 다운로드 진행중...")
                                    time.sleep(2)  # 다운로드 시작 대기
                                    self.driver.close()
                                except Exception as e:
                                    print("새 탭 처리 중 오류:", e)
                        try:
                            self.driver.switch_to.window(original_handle)
                        except Exception as e:
                            print("원래 창으로 전환 실패:", e)
                    else:
                        print("새 탭이 열리지 않음, 클릭 후 다운로드가 진행되었을 가능성이 있음.")
                    time.sleep(1)
                    # 다운로드 완료 후, 파일명을 target_file_name(공백이 '+'로 대체된 이름)으로 변경
                    self.wait_for_download_and_rename(download_path, file_name)
            except Exception as e:
                print("파일 다운로드 처리 실패:", e)
        for file_name in docx_files:
            print(f"{file_name} 파일 다운로드 요청 완료.")


class Document:
    """
    다양한 소스(API, 인터넷 자료, PDF 등)에서 수집된 데이터를 통합적으로 다룰 수 있는 Document 객체입니다.

    Attributes:
        content (Any): 크롤링 또는 수집한 객체 데이터.
        source (Any): 원본 데이터 또는 자료의 출처.
        attached_file (List[Any]): 연관된 파일들 (예: 이미지, 기타 연계 파일 등).
    """

    def __init__(self, content: Any, source: Any, attached_file: Optional[List[Any]] = None):
        self.content = content
        self.source = source
        self.attached_file = attached_file if attached_file is not None else []

    def __repr__(self):
        return (f"Document(content={self.content!r}, "
                f"source={self.source!r}, "
                f"attached_file={self.attached_file!r})")


if __name__ == "__main__":
    notion_url = "https://sincere-nova-ec6.notion.site/a8bbcb69d87c4c19aabee16c6a178286"
    # data = crawl_notion_page_with_toggles(notion_url)
    crawler = NotionCrawler(webdriver.Chrome())
    # data = crawl_notion_page_with_toggles(notion_url)
    document = crawler.read(notion_url)
    if document is not None:
        print("\n크롤링 완료!")
