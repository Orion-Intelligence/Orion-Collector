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


class _ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd.onion"

    @property
    def base_url(self) -> str:

        return "http://ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd.onion"

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

        return "http://ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:
            base_url = self.base_url
            all_hrefs = []

            current_page = 1
            while current_page <= 18:
                page.goto(f"{base_url}/?page={current_page}")
                page.wait_for_selector('.col-md-3.ps-lg-0.text-right.mb-2')

                href_elements = page.query_selector_all('.col-md-3.ps-lg-0.text-right.mb-2 a.learn_more')
                if not href_elements:
                    break

                for element in href_elements:
                    href = element.get_attribute("href")
                    if href and href not in all_hrefs:
                        absolute_href = f"{base_url}{href}" if href.startswith('/') else href
                        all_hrefs.append(absolute_href)

                current_page += 1

            for href in all_hrefs:
                try:
                    page.goto(href)
                    page.wait_for_selector('.item_box')

                    item_boxes = page.query_selector_all('.item_box')
                    for box in item_boxes:
                        images = []
                        image_elements = box.query_selector_all('.item_box_photos-photo a')
                        for img in image_elements:
                            img_href = img.get_attribute("href")
                            if img_href:
                                absolute_img_href = f"{base_url}{img_href}" if img_href.startswith('/') else img_href
                                images.append(absolute_img_href)

                        description_element = box.query_selector('.col-md-8.col-xl-6')
                        description = description_element.inner_text().strip() if description_element else ""

                        title_element = page.query_selector('.page_title')
                        title = title_element.inner_text().strip() if title_element else ""

                        company_url = ""
                        company_url_element = box.query_selector('.item_box-info__link')
                        if company_url_element:
                            company_url = company_url_element.get_attribute("href")

                        date = ""
                        date_element = box.query_selector('.item_box-info__item img[src="/images/clock.png"] + div')
                        if date_element:
                            date = date_element.inner_text().strip()

                        important_content = " ".join(description.split()[:500])

                        card_data = leak_model(
                            m_screenshot=helper_method.get_screenshot_base64(page, title),
                            # m_screenshot="",
                            m_title=title,
                            m_url=href,
                            m_base_url=base_url,
                            m_content=description,
                            m_network=helper_method.get_network_type(base_url),
                            m_important_content=important_content,
                            m_content_type=["leaks"],
                            m_weblink=[company_url] if company_url else [],
                            m_logo_or_images=images,
                            m_leak_date=helper_method.extract_and_convert_date(date),
                        )

                        entity_data = entity_model()
                        self.append_leak_data(card_data, entity_data)

                except Exception as e:
                    print(f"Error processing href {href}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error in parse_leak_data: {str(e)}")