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


class _hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd.onion/list"

    @property
    def base_url(self) -> str:
        return "http://hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        page.wait_for_selector("a.break-words")
        card_links = [
            self.base_url + anchor.get_attribute("href")
            for anchor in page.query_selector_all("a.break-words")
            if anchor and anchor.get_attribute("href")
        ]
        for card_link in card_links:
            page.goto(card_link)
            page.wait_for_selector("div.text-lg.font-bold.break-words")

            company_name = page.query_selector("div.text-lg.font-bold.break-words").inner_text() if page.query_selector("div.text-lg.font-bold.break-words") else ""
            weblink = page.query_selector("div.truncate a").get_attribute("href") if page.query_selector("div.truncate a") else ""
            description = page.query_selector("div.whitespace-pre-line.break-words").inner_text() if page.query_selector("div.whitespace-pre-line.break-words") else ""
            download_link = page.query_selector("div.flex a.truncate").get_attribute("href") if page.query_selector("div.flex a.truncate") else ""
            leak_size = page.query_selector("div:has-text('Leaked size') span.font-bold.whitespace-pre-line").inner_text() if page.query_selector("div:has-text('Leaked size') span.font-bold.whitespace-pre-line") else ""

            m_content = description

            card_data = leak_model(
                m_title=company_name,
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot=helper_method.get_screenshot_base64(page,company_name),
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=m_content,
                m_weblink=[weblink],
                m_dumplink=[download_link],
                m_content_type=["leaks"],
                m_data_size=leak_size
            )

            entity_data = entity_model(
                m_email_addresses=helper_method.extract_emails(m_content),
                m_phone_numbers=helper_method.extract_phone_numbers(m_content),
            )

            self.append_leak_data(card_data, entity_data)