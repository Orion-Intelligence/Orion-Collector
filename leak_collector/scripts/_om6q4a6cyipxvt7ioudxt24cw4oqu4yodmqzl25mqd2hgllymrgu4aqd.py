from abc import ABC
from time import sleep
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _om6q4a6cyipxvt7ioudxt24cw4oqu4yodmqzl25mqd2hgllymrgu4aqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_om6q4a6cyipxvt7ioudxt24cw4oqu4yodmqzl25mqd2hgllymrgu4aqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://om6q4a6cyipxvt7ioudxt24cw4oqu4yodmqzl25mqd2hgllymrgu4aqd.onion"

    @property
    def base_url(self) -> str:
        return "http://om6q4a6cyipxvt7ioudxt24cw4oqu4yodmqzl25mqd2hgllymrgu4aqd.onion"

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
        return "https://breachforums.st/User-Anubis-media"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:
            page.wait_for_selector("div.col-sm-4.p-2")

            open_links = []
            cards = page.query_selector_all("div.col-sm-4.p-2")
            for card_index, card in enumerate(cards, start=1):
                try:
                    open_button = card.query_selector("a.btn")
                    weblink = open_button.get_attribute("href") if open_button else None
                    if weblink:
                        open_links.append(weblink)
                except Exception as e:
                    print(f"An error occurred while collecting link for card {card_index}: {e}")

            for link_index, weblink in enumerate(open_links, start=1):
                try:
                    page.goto(weblink)

                    page.wait_for_selector("div.bg-secondary h1", timeout=15000)
                    sleep(5)

                    download_button = page.query_selector("div.col-sm-5 a.btn")
                    dumplink = download_button.get_attribute("href") if download_button else None

                    title_element = page.query_selector("div.bg-secondary h1")
                    title = title_element.inner_text().strip() if title_element else None

                    description_element = page.query_selector("div.ql-editor")
                    description = description_element.inner_text().strip() if description_element else None

                    website_element = description_element.query_selector("a") if description_element else None
                    website = website_element.get_attribute("href") if website_element else None

                    websites = [website] if website else []

                    image_elements = page.query_selector_all("img.clickable-image")
                    image_links = [
                        img.get_attribute("src") for img in image_elements if img.get_attribute("src")
                    ]

                    card_data = leak_model(
                        m_title=title,
                        m_url=page.url,
                        m_base_url=self.base_url,
                        m_screenshot="",
                        m_content=description,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_important_content=description,
                        m_weblink=[weblink] if weblink else [],
                        m_dumplink=[dumplink] if dumplink else [],
                        m_content_type=["leaks"],
                        m_logo_or_images=image_links,
                        m_websites=websites,
                    )
                    entity_data = entity_model(
                        m_email=helper_method.extract_emails(description) if description else [],
                        m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                        m_company_name=title,
                    )
                    self.append_leak_data(card_data, entity_data)

                except Exception as e:
                    print(f"An error occurred while processing link {link_index}: {weblink} - {e}")

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")