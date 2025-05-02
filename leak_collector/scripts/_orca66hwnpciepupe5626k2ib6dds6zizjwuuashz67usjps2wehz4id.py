import datetime
from abc import ABC
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import CUSTOM_SCRIPT_REDIS_KEYS
from urllib.parse import urljoin

from crawler.crawler_services.shared.helper_method import helper_method


class _orca66hwnpciepupe5626k2ib6dds6zizjwuuashz67usjps2wehz4id(leak_extractor_interface, ABC):
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
            cls._instance = super(_orca66hwnpciepupe5626k2ib6dds6zizjwuuashz67usjps2wehz4id, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://orca66hwnpciepupe5626k2ib6dds6zizjwuuashz67usjps2wehz4id.onion"

    @property
    def base_url(self) -> str:
        return "http://orca66hwnpciepupe5626k2ib6dds6zizjwuuashz67usjps2wehz4id.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://orca66hwnpciepupe5626k2ib6dds6zizjwuuashz67usjps2wehz4id.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    @staticmethod
    def safe_find(page, selector, attr=None):
        try:
            element = page.query_selector(selector)
            if element:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None

    def parse_leak_data(self, page: Page):
        try:

            page.goto(self.seed_url)
            page.wait_for_load_state('load')


            card_links = page.query_selector_all("a.blog__card-btn.--button")
            if not card_links:
                print("No card links found on the page.")
                return

            card_urls = [urljoin(self.base_url, link.get_attribute("href")) for link in card_links]


            for card_url in card_urls:

                page.goto(card_url)
                page.wait_for_load_state('load')


                page_html = page.content()
                self.soup = BeautifulSoup(page_html, 'html.parser')


                card_inner = self.soup.select_one("div.card__inner")
                if not card_inner:
                    print(f"No card inner found on the page: {card_url}")
                    continue


                description = self.safe_find(page, "div.card__description-content", attr=None)
                company_url = self.safe_find(page, "a.card__info-text.--card__info-text-link", attr="href")
                download_url = self.safe_find(page, "a.card__download.--button", attr="href")
                card_title = self.safe_find(page, "h1.card__title", attr=None)


                number_of_files = None
                date_of_publication = None

                info_items = card_inner.select("div.card__info-item")
                for item in info_items:
                    title_elem = item.select_one("h2.card__info-item-title")
                    if not title_elem:
                        continue

                    title_text = title_elem.get_text(strip=True).lower()
                    if "date of publication" in title_text:
                        date_elem = item.select_one("p.card__info-text")
                        if date_elem:
                            date_of_publication = date_elem.get_text(strip=True)
                    elif "number of files" in title_text:
                        number_elem = item.select_one("p.card__info-text")
                        if number_elem:
                            number_of_files = number_elem.get_text(strip=True)

                if date_of_publication is None:
                    date_of_publication = ""

                card_data = leak_model(
                    m_screenshot=helper_method.get_screenshot_base64(page, card_title),
                    m_title=card_title,
                    m_url=self.base_url,
                    m_weblink=[company_url] if company_url else [],
                    m_dumplink=[download_url],
                    m_network=helper_method.get_network_type(self.base_url),
                    m_base_url=self.base_url,
                    m_content=description + " " + self.base_url + " " + page.url,
                    m_important_content = description,
                    m_content_type=["leaks"],
                    m_data_size=number_of_files,
                    m_leak_date=datetime.datetime.strptime(date_of_publication, '%d/%m/%Y').date(),
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(description) if description else [],
                    m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                    m_company_name=card_title,
                )

                self.append_leak_data(card_data, entity_data)

        except Exception as ex:
            print(f"An error occurred: {ex}")