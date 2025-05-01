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
import time
from datetime import datetime

class _34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad(leak_extractor_interface, ABC):
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
            cls._instance = super(_34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion/leaks"

    @property
    def base_url(self) -> str:
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion"

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
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion/contact"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:
            current_page = 1
            max_pages = 3

            while current_page <= max_pages:
                next_url = f"{self.seed_url}/{current_page}"
                page.goto(next_url)
                page.wait_for_load_state('networkidle')
                time.sleep(2)
                posts = page.query_selector_all('div.py-6.relative')
                if not posts:
                    break

                for post in posts:
                    try:
                        date_element = post.query_selector('time')
                        publication_date = None

                        if date_element:
                            raw_date = date_element.text_content().strip()
                            try:
                                parsed_date = datetime.strptime(raw_date, '%b %d, %Y, %H:%M')
                                publication_date = parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                publication_date = None


                        title_element = post.query_selector('h2')
                        title = title_element.inner_text().strip() if title_element else "No Title"
                        title_parts = title.split('|')
                        company_name = title_parts[0].strip() if len(title_parts) > 0 else "No Company"
                        location = title_parts[1].strip() if len(title_parts) > 1 else "No Location"


                        description_element = post.query_selector('.parsed-post-text')
                        description = description_element.inner_text().strip() if description_element else "No Description"

                        if not title_element and not description_element:
                            continue

                        industry = "No Industry"
                        if description_element:
                            industry_element = description_element.query_selector('p')  # Select the first <p> tag
                            if industry_element:
                                industry = industry_element.inner_text().strip()

                        file_links = []
                        file_elements = post.query_selector_all('ul.parsed-post-text li a')
                        for file_element in file_elements:
                            file_link = file_element.get_attribute('href')
                            if file_link:
                                file_links.append(file_link)


                        size_element = post.query_selector(
                            'span.inline-block.ml-1\\.5.text-slate-600.font-bold'
                        )
                        data_size = size_element.inner_text().strip() if size_element else "No Size"


                        card_data = leak_model(
                            m_title=title,
                            m_url=page.url,
                            m_base_url=self.base_url,
                            m_screenshot=helper_method.get_screenshot_base64(page,title),
                            m_content=description,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_important_content=description,
                            m_dumplink=file_links,
                            m_content_type=["leaks"],
                            m_data_size=data_size,
                            m_leak_date=publication_date,
                        )

                        entity_data = entity_model(
                            m_email_addresses=helper_method.extract_emails(description),
                            m_phone_numbers=helper_method.extract_phone_numbers(description),
                            m_location_info=[location],
                            m_company_name=company_name,
                            m_industry=industry,
                        )

                        self.append_leak_data(card_data, entity_data)

                    except Exception as post_error:
                        print(f"Error parsing post: {post_error}")

                current_page += 1

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")