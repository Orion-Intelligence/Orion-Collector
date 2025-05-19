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
class _imncrewwfkbjkhr2oylerfm5qtbzfphhmpcfag43xc2kfgvluqtlgoid(leak_extractor_interface, ABC):
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
            cls._instance = super(_imncrewwfkbjkhr2oylerfm5qtbzfphhmpcfag43xc2kfgvluqtlgoid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://imncrewwfkbjkhr2oylerfm5qtbzfphhmpcfag43xc2kfgvluqtlgoid.onion/"

    @property
    def base_url(self) -> str:
        return "http://imncrewwfkbjkhr2oylerfm5qtbzfphhmpcfag43xc2kfgvluqtlgoid.onion/"

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
        return "http://imncrewwfkbjkhr2oylerfm5qtbzfphhmpcfag43xc2kfgvluqtlgoid.onion/"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):

        page.wait_for_selector("div.block")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        card_blocks = soup.find_all("div", class_="block")

        for card in card_blocks:
            title_tag = card.find("h3", class_="yellow-text")
            m_title = title_tag.get_text(strip=True) if title_tag else ""

            desc_tag = card.find("p")
            m_content = desc_tag.get_text(strip=True) if desc_tag else ""

            words = m_content.split()
            if len(words) > 500:
                important_content = ' '.join(words[:500])
            else:
                important_content = m_content

            download_link = ""
            spoiler_content = card.find("div", class_="spoiler-content")
            if spoiler_content:
                a_tag = spoiler_content.find("a", href=True)
                if a_tag:
                    download_link = a_tag["href"]

            image_urls = []
            images_div = card.find("div", class_="images")
            if images_div:
                for img_tag in images_div.find_all("img", src=True):
                    image_urls.append(img_tag["src"])

            card_data = leak_model(
                m_title=m_title,
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot=helper_method.get_screenshot_base64(page,m_title,self.base_url),
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=important_content,
                m_logo_or_images=image_urls,
                m_dumplink=[download_link] if download_link else [],
                m_content_type=["leaks"],

            )

            entity_data = entity_model(
                m_email_addresses=helper_method.extract_emails(m_content),
                m_phone_numbers=helper_method.extract_phone_numbers(m_content),
            )

            self.append_leak_data(card_data, entity_data)