from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.shared.helper_method import helper_method


class _worldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid(leak_extractor_interface, ABC):
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
            cls._instance = super(_worldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://worldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid.onion/companies/0886726786"

    @property
    def base_url(self) -> str:
        return "https://worldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.NONE, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: str, default_value, expiry: int = None):

        return self._redis_instance.invoke_trigger(command, [key + self.__class__.__name__, default_value, expiry])

    def contact_page(self) -> str:
        return "https://x.com/share?url=https%3A%2F%2Fworldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid.onion%2Fcompanies%2F0886726786"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        
        m_content = ""

        card_data = leak_model(
            m_title=page.title(),
            m_url=page.url,
            m_base_url=self.base_url,
            m_screenshot="",
            m_content=m_content,
            m_network=helper_method.get_network_type(self.base_url),
            m_important_content=m_content,
            m_weblink=[],
            m_dumplink=[],
            m_content_type=["leaks"],
        )

        entity_data = entity_model(
            m_email=helper_method.extract_emails(m_content),
            m_phone_numbers=helper_method.extract_phone_numbers(m_content),
        )

        self.append_leak_data(card_data, entity_data)
