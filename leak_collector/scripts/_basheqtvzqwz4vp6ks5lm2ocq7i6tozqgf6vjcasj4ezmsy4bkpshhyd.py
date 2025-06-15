import time
from abc import ABC
from datetime import datetime
from typing import List

from playwright.sync_api import Page

from crawler.constants.constant import RAW_PATH_CONSTANTS
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import CUSTOM_SCRIPT_REDIS_KEYS, REDIS_COMMANDS
from crawler.crawler_services.shared.helper_method import helper_method


class _basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd(leak_extractor_interface, ABC):
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
            cls._instance = super(_basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/"

    @property
    def base_url(self) -> str:

        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/"

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
        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/contact_us.php"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        page.wait_for_selector('.main__contant')

        card_elements = page.query_selector_all('.segment.published')
        card_urls = [card.get_attribute('onclick').split("window.location.href='")[1].split("'")[0] for card in
                     card_elements]

        error_count = 0

        for card_url in card_urls:
            try:
                page.goto(self.base_url + card_url)
                page.wait_for_selector('.main__contant')
                time.sleep(2)

                title_element = page.query_selector('.offer__text')
                title = title_element.inner_text().strip() if title_element else "N/A"

                deadline_element = page.query_selector('.deadline:first-of-type')
                deadline = deadline_element.inner_text().replace("Deadline: ",
                                                                 "").strip() if deadline_element else "N/A"
                deadline = datetime.strptime(deadline.split()[0], '%Y/%m/%d').date()

                country_element = page.query_selector('.count__text')
                country = country_element.inner_text().strip() if country_element else "N/A"

                description_element = page.query_selector('.dsc__text')
                description = description_element.inner_text().strip() if description_element else "N/A"

                image_urls = []
                images = page.query_selector_all('img')
                for img in images:
                    src = img.get_attribute('src')
                    if src:
                        full_src = self.base_url + src if not src.startswith('http') else src
                        image_urls.append(full_src)

                dumps = []
                links = page.query_selector_all('a')
                for link in links:
                    div_element = link.query_selector('.segment__block__small.published.download')
                    if div_element:
                        href = link.get_attribute('href')
                        if href:
                            dumps.append(href)

                web_link = []
                for link in links:
                    div_element = link.query_selector('.segment__block.active.download')
                    if div_element:
                        href = link.get_attribute('href')
                        if href:
                            full_href = self.base_url + href if not href.startswith('http') else href
                            web_link.append(full_href)

                is_crawled = int(
                    self.invoke_db(REDIS_COMMANDS.S_GET_INT, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED.value + title, 0,
                                   RAW_PATH_CONSTANTS.HREF_TIMEOUT))
                ref_html = None
                if is_crawled != -1 and is_crawled < 5:
                    ref_html = helper_method.extract_refhtml(title)
                    if ref_html:
                        self.invoke_db(REDIS_COMMANDS.S_SET_INT, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED.value + title, -1,
                                       RAW_PATH_CONSTANTS.HREF_TIMEOUT)
                    else:
                        self.invoke_db(REDIS_COMMANDS.S_SET_INT, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED.value + title,
                                       is_crawled + 1, RAW_PATH_CONSTANTS.HREF_TIMEOUT)

                card_data = leak_model(
                    m_ref_html=ref_html,
                    m_screenshot=helper_method.get_screenshot_base64(page, None, self.base_url),
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_content=description + " " + self.base_url + " " + page.url,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description,
                    m_dumplink=dumps,
                    m_weblink=web_link,
                    m_leak_date=deadline,
                    m_logo_or_images=image_urls,
                    m_content_type=["leaks"],
                )

                entity_data = entity_model(
                    m_email=helper_method.extract_emails(description),
                    m_country_name=country,
                    m_location=[country],
                    m_ip=[title],
                    m_team="bashe"
                )
                entity_data = helper_method.extract_entities(description, entity_data)

                self.append_leak_data(card_data, entity_data)
                error_count = 0

            except Exception:
                error_count += 1
                if error_count >= 3:
                    break
