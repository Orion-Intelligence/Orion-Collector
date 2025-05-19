from abc import ABC
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad(leak_extractor_interface, ABC):
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
            cls._instance = super(_gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad.onion"

    @property
    def base_url(self) -> str:
        return "http://gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad.onion"

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
        return "http://jzbhtsuwysslrzi2n5is3gmzsyh6ayhm7jt3xowldhk7rej4dqqubxqd.onion/login"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:
            page.wait_for_selector("#wrapper")
            main_page_html = page.content()

            soup = BeautifulSoup(main_page_html, "html.parser")
            company_blocks = soup.select("div[style*='padding: 10px;']")

            title_links = []
            for block_index, block in enumerate(company_blocks, start=1):
                title_el = block.select_one(".companyName h2 a")
                title = title_el.text.strip() if title_el else None
                dumplink = title_el["href"] if title_el and "href" in title_el.attrs else None

                industry_el = block.select_one(".industry")
                industry = industry_el.text.replace("Industry:", "").strip() if industry_el else None

                location_el = block.select_one(".location")
                location = location_el.text.replace("Location:", "").strip() if location_el else None

                publish_date_el = block.select_one(".dueDate")
                raw_publish_date = publish_date_el.text.replace("Publish Date:",
                                                                "").strip() if publish_date_el else None
                publish_date = None
                if raw_publish_date and raw_publish_date not in ["Expired", "---"]:
                    try:
                        publish_date = datetime.strptime(
                            raw_publish_date.replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""),
                            "%B %d"
                        ).replace(year=datetime.utcnow().year).strftime("%Y-%m-%d")
                    except ValueError:
                        pass

                weblink_el = block.select_one(".dueDate a")
                weblink = weblink_el["href"] if weblink_el and "href" in weblink_el.attrs else None

                title_links.append({
                    "block_index": block_index,
                    "title": title,
                    "industry": industry,
                    "location": location,
                    "publish_date": publish_date,
                    "weblink": weblink,
                    "dumplink": dumplink,
                    "description": f"Title: {title}\nIndustry: {industry}\nLocation: {location}\nPublish Date: {raw_publish_date}"
                })

            for title_data in title_links:
                card_data = leak_model(
                    m_title=title_data["title"],
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot="",
                    m_content=title_data["description"],
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=title_data["description"],
                    m_weblink=[title_data["weblink"]] if title_data["weblink"] else [],
                    m_dumplink=[title_data["dumplink"]] if title_data["dumplink"] else [],
                    m_content_type=["leaks"],
                    m_leak_date=title_data["publish_date"],
                )
                entity_data = entity_model(
                    m_email=helper_method.extract_emails(title_data["description"]),
                    m_phone_numbers=helper_method.extract_phone_numbers(title_data["description"]),
                    m_location=[title_data["location"]] if title_data["location"] else [],
                    m_country_name=title_data["location"],
                    m_company_name=title_data["title"],
                    m_industry=title_data["industry"]
                )
                self.append_leak_data(card_data, entity_data)

            with open("main_page.html", "w", encoding="utf-8") as f:
                f.write(main_page_html)

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")