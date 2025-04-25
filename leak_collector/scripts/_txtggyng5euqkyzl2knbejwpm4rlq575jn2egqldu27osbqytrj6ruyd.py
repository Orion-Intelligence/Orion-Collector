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


class _txtggyng5euqkyzl2knbejwpm4rlq575jn2egqldu27osbqytrj6ruyd(leak_extractor_interface, ABC):
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
            cls._instance = super(_txtggyng5euqkyzl2knbejwpm4rlq575jn2egqldu27osbqytrj6ruyd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://txtggyng5euqkyzl2knbejwpm4rlq575jn2egqldu27osbqytrj6ruyd.onion/articles"

    @property
    def base_url(self) -> str:

        return "http://txtggyng5euqkyzl2knbejwpm4rlq575jn2egqldu27osbqytrj6ruyd.onion/articles"

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

        return "http://txtggyng5euqkyzl2knbejwpm4rlq575jn2egqldu27osbqytrj6ruyd.onion/articles"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:

            page.goto(self.seed_url)

            page.wait_for_selector('.card-body')


            card_elements = page.query_selector_all('.card-body')


            for card in card_elements:
                try:

                    title_element = card.query_selector('h5.card-title')
                    title = title_element.inner_text().strip() if title_element else ""

                    description_element = card.query_selector('p.card-text:has(strong:has-text("Description:"))')
                    description = ""
                    if description_element:

                        description = description_element.inner_text().replace("Description:", "").strip()

                    publication_time_element = card.query_selector('span[data-countdown-publication-time]')
                    publication_time = publication_time_element.get_attribute(
                        'data-countdown-publication-time') if publication_time_element else ""


                    revenue_element = card.query_selector('p.card-text:has(strong:has-text("Revenue:"))')
                    revenue = ""
                    if revenue_element:

                        revenue = revenue_element.inner_text().replace("Revenue:", "").strip()


                    company_name_element = card.query_selector('p.card-text:has(strong:has-text("Company name:"))')
                    company_name = ""
                    if company_name_element:

                        company_name = company_name_element.inner_text().replace("Company name:", "").strip()


                    show_leaks_element = card.query_selector('a.btn.btn-primary')
                    show_leaks_link = show_leaks_element.get_attribute('href') if show_leaks_element else ""



                    if show_leaks_link and not show_leaks_link.startswith('http'):
                        if show_leaks_link.startswith('/'):
                            show_leaks_link = f"{self.base_url}{show_leaks_link}"
                        else:
                            show_leaks_link = f"{self.base_url}/{show_leaks_link}"


                    card_data = leak_model(
                        m_screenshot=helper_method.get_screenshot_base64(page, title),
                        m_title=title,
                        m_url=show_leaks_link,
                        m_base_url=self.base_url,
                        m_content=f"Description: {description}, Revenue: {revenue}, Company Name: {company_name}",
                        m_network=helper_method.get_network_type(self.base_url),
                        m_important_content=f"Description: {description}, Revenue: {revenue}, Company Name: {company_name}",
                        m_content_type=["leaks"],

                    )

                    entity_data = entity_model()
                    self.append_leak_data(card_data, entity_data)

                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error in parse_leak_data: {str(e)}")