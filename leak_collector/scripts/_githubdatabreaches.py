from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method
from bs4 import BeautifulSoup


class _githubdatabreaches(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):

        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):

        self.callback = callback

    def __new__(cls, callback=None):

        if cls._instance is None:
            cls._instance = super(_githubdatabreaches, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://github.com/doormanBreach/DataBreaches"

    @property
    def base_url(self) -> str:
        return "https://github.com/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: str, default_value, expiry: int = None):
        return self._redis_instance.invoke_trigger(command, [key + self.__class__.__name__, default_value, expiry])

    def contact_page(self) -> str:
        return "https://www.iana.org/help/example-domains"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):

        page.wait_for_selector('.react-directory-truncate a')
        soup = BeautifulSoup(page.content(), 'html.parser')
        link_tags = soup.select('.react-directory-truncate a')
        md_links = []
        for link in link_tags:
            href = link.get('href', '')
            if href.endswith('.md') and '/blob/' in href:
                md_links.append('https://github.com' + href)

        print(md_links)

        for md_url in md_links:
            page.goto(md_url)
            page.wait_for_selector('article.markdown-body')
            file_soup = BeautifulSoup(page.content(), 'html.parser')
            article = file_soup.find('article', class_='markdown-body')
            if not article:
                continue

            # Title (first h1)
            title = article.find('h1').get_text(strip=True) if article.find('h1') else ""
            print(title)
            # Description and Date
            description = ""
            date = ""
            desc_h2 = article.find('h2', string=lambda s: s and 'Description' in s)
            if desc_h2:
                p_date = desc_h2.find_next_sibling('p')
                date = p_date.get_text(strip=True) if p_date else ""
                p_desc = p_date.find_next_sibling('p') if p_date else None
                description = p_desc.get_text(strip=True) if p_desc else ""
            print(description)

            # Breached Data
            breached_data = ""
            bd_h2 = article.find('h2', string=lambda s: s and 'Breached data' in s)
            if bd_h2:
                p_bd = bd_h2.find_next_sibling('p')
                breached_data = p_bd.get_text(strip=True) if p_bd else ""
            print("Breached data",breached_data)

            # Download Links
            download_links = []
            download_h2 = article.find('h2', string=lambda s: s and 'Free download Link' in s)
            if download_h2:
                p_links = download_h2.find_next_sibling('p')
                if p_links:
                    for a in p_links.find_all('a', href=True):
                        download_links.append(a['href'])
                for a in download_h2.find_all_next('a', href=True):
                    if a['href'].startswith('http'):
                        download_links.append(a['href'])
                    # Stop if we hit another heading
                    if a.find_previous('h2') is not download_h2:
                        break
                download_links = list(dict.fromkeys(download_links))
                print(download_links)

            m_content = f"Date: {date}\nDescription: {description}\nBreached data: {breached_data}\nDownload links: {download_links}"

            card_data = leak_model(
                m_title=title,
                m_url=md_url,
                m_base_url=self.base_url,
                m_screenshot="",
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=description,
                m_weblink=[],
                m_dumplink=download_links,
                m_content_type=["leaks"],
            )

            entity_data = entity_model(
                m_email=helper_method.extract_emails(m_content),
                m_phone_numbers=helper_method.extract_phone_numbers(m_content),
            )

            self.append_leak_data(card_data, entity_data)