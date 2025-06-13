from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.shared.helper_method import helper_method
import re

class _tp5cwh6d2b5hekcg6jlhoe6mawa7dlwiv47epvnfmzuaaur2dnaa3uid(leak_extractor_interface, ABC):
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
            cls._instance = super(_tp5cwh6d2b5hekcg6jlhoe6mawa7dlwiv47epvnfmzuaaur2dnaa3uid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "tp5cwh6d2b5hekcg6jlhoe6mawa7dlwiv47epvnfmzuaaur2dnaa3uid"

    @property
    def base_url(self) -> str:
        return "tp5cwh6d2b5hekcg6jlhoe6mawa7dlwiv47epvnfmzuaaur2dnaa3uid"

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
        return "http://tp5cwh6d2b5hekcg6jlhoe6mawa7dlwiv47epvnfmzuaaur2dnaa3uid.onion/"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        cards = page.query_selector_all('div.center1')

        for card in cards:
            date = ""
            weblink = ""
            country = ""
            title = ""
            description = ""
            image_urls = []
            dumps = ""

            title_element = card.query_selector("#sonTwo")
            if title_element:
                title = title_element.inner_text().strip()

            text_color_element = card.query_selector("#TextColor")
            if text_color_element:
                text_content = text_color_element.inner_text().strip()

                date_match = re.search(r'Published (\d{1,2}/\d{1,2}/\d{4})', text_content)
                if date_match:
                    date = date_match.group(1)

                country_match = re.search(r'place</i>([A-Z]{2})', card.inner_html())
                if country_match:
                    country = country_match.group(1)

                weblink_match = re.search(r'<i class="fa fa-chain"></i>([^\s<]+)', card.inner_html())
                if weblink_match:
                    weblink = weblink_match.group(1)

                description_lines = []
                lines = text_content.split('\n')
                capture = False
                for line in lines:
                    if 'place' in line and country in line:
                        capture = True
                        continue
                    if capture and 'Here is an image of what you have downloaded:' in line:
                        break
                    if capture and line.strip():
                        description_lines.append(line.strip())
                description = ' '.join(description_lines)

                image_links = text_color_element.query_selector_all('a')
                for link in image_links:
                    href = link.get_attribute('href')
                    if href and (href.endswith('.png') or href.endswith('.PNG')):
                        image_urls.append(href)

                text_nodes = text_content.split('\n')
                for line in text_nodes:
                    if line.startswith('http') and (line.endswith('.png') or line.endswith('.PNG')):
                        image_urls.append(line.strip())

                download_link = text_color_element.query_selector('a')
                if download_link:
                    href = download_link.get_attribute('href')
                    link_text = download_link.inner_text().strip()
                    if href and (link_text == 'Read more' or link_text == 'Download The Files'):
                        dumps = href

            card_data = leak_model(
                m_title=title,
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot="",
                m_content=description,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=description,
                m_weblink=[weblink] if weblink else [],
                m_dumplink=[dumps] if dumps else [],
                m_content_type=["leaks"],
                m_leak_date=helper_method.extract_and_convert_date(date),
                m_logo_or_images=image_urls
            )

            entity_data = entity_model(
                m_email=helper_method.extract_emails(description),
                m_phone_numbers=helper_method.extract_phone_numbers(description),
                m_country_name=country
            )

            # Append data for this card
            self.append_leak_data(card_data, entity_data)
