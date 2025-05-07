from abc import ABC
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method

class _weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd(leak_extractor_interface, ABC):
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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"

    @property
    def base_url(self) -> str:
        return "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config = FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command:int, key: str, default_value):
        return self._redis_instance.invoke_trigger(command, [key + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/?contact"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page:Page ):

        pagination_links = self.soup.select("div.pagination a")
        page_urls = [urljoin(self.seed_url, link['href']) for link in pagination_links]

        for page_url in page_urls:
            page.goto(page_url, wait_until="networkidle")
            self.soup = BeautifulSoup(page.content(), 'html.parser')

            cards = self.soup.find_all(class_="card")
            for card in cards:
                title = card.find(class_="title")
                text_elements = card.find_all(class_="text")
                link_elements = card.find_all(class_="links")

                title_text = helper_method.clean_text(title.get_text(strip=True)) if title else ""
                content = ' '.join(helper_method.clean_text(text.get_text(strip=True)) for text in text_elements if text)
                dumplinks = [urljoin(self.base_url, link.a['href']) for link in link_elements if link and link.a]
                website_element = card.select_one(".url a")
                website_url = website_element["href"].strip() if website_element and website_element.has_attr("href") else ""
                weblinks = [website_url] if website_url else ([urljoin(self.base_url, title.a['href'])] if title and title.a else [])

                ref_html = None
                if weblinks and len(weblinks)>0:
                    is_crawled = self.invoke_db(REDIS_COMMANDS.S_GET_BOOL, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED.value + weblinks[0], False)
                    if not is_crawled:
                        ref_html = helper_method.extract_refhtml(weblinks[0])
                        if ref_html:
                            self.invoke_db(REDIS_COMMANDS.S_SET_BOOL, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED.value + weblinks[0], True)

                card_data = leak_model(
                    m_ref_html=ref_html,
                    m_screenshot=helper_method.get_screenshot_base64(page, title_text),
                    m_title=title_text,
                    m_url=page_url,
                    m_base_url=self.base_url,
                    m_content=content + " " + self.base_url + " " + page_url,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=content,
                    m_weblink=weblinks,
                    m_dumplink=dumplinks,
                    m_content_type=["leaks"]
                )

                entity_data = entity_model(
                    m_company_name=title_text,
                    m_ip=weblinks,
                    m_email_addresses= helper_method.extract_emails(content),
                )
                self.append_leak_data(card_data, entity_data)
