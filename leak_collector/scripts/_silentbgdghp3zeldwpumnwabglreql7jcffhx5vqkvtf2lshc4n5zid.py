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

class _silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid(leak_extractor_interface, ABC):
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
            cls._instance = super(_silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/"

    @property
    def base_url(self) -> str:
            return "http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/"

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
        return "http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        page.wait_for_timeout(5000)

        content = page.content()
        self.soup = BeautifulSoup(content, 'html.parser')

        cards = self.soup.find_all('div', class_='_companieInfoCard_48fxr_1')

        for card in cards:

            title = card.find('div', class_='_companyName_48fxr_51')
            title = title.text.strip() if title else None

            country_name = card.find('span', class_='_countryName_48fxr_223')
            country_name = country_name.text.strip() if country_name else None

            custom_link = card.find('a', class_='_productLink_48fxr_147')
            custom_link = custom_link['href'] if custom_link else None

            info_cards = card.find_all('div', class_='_companyCardInfo_48fxr_63')

            revenue = None
            employees = None
            disclosures = None

            for info in info_cards:
                spans = info.find_all('span')
                if len(spans) >= 2:
                    label = spans[0].text.strip()
                    value = spans[1].text.strip()

                    if label == "Revenue":
                        revenue = value
                    elif label == "Employees":
                        employees = value
                    elif label == "Disclosures":
                        disclosures = value


            m_content = f"Title: {title}, Country: {country_name}, Revenue: {revenue}, Employees: {employees}, Disclosures: {disclosures}"

            card_data = leak_model(
                m_title=title,
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot="",
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=m_content,
                m_weblink=[custom_link],
                m_dumplink=[page.url],
                m_content_type=["leaks"],

            )

            entity_data = entity_model(

            )

            self.append_leak_data(card_data, entity_data)


