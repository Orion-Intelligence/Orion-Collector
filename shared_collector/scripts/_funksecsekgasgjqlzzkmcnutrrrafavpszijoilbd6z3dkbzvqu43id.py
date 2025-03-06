from abc import ABC
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from urllib.parse import urljoin
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _funksecsekgasgjqlzzkmcnutrrrafavpszijoilbd6z3dkbzvqu43id(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self.soup = None
        self._card_data = []
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_funksecsekgasgjqlzzkmcnutrrrafavpszijoilbd6z3dkbzvqu43id, cls).__new__(cls)
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://funksecsekgasgjqlzzkmcnutrrrafavpszijoilbd6z3dkbzvqu43id.onion"

    @property
    def base_url(self) -> str:
        return "http://funksecsekgasgjqlzzkmcnutrrrafavpszijoilbd6z3dkbzvqu43id.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return self.seed_url

    def safe_find(self, page, selector, attr=None):

        try:
            element = page.locator(selector).first
            if element.count() > 0:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None

    def parse_leak_data(self, page: Page):
        try:
            page.goto(self.seed_url)
            page.wait_for_load_state('load')

            page_html = page.content()
            self.soup = BeautifulSoup(page_html, 'html.parser')

            # Extract product links
            product_links = []
            product_cards = self.soup.select("a.product-card")

            for card in product_cards:
                item_url = card.get('href')
                if item_url and not item_url.startswith(('http://', 'https://')):
                    item_url = urljoin(self.base_url, item_url)
                product_links.append(item_url)

            # Visit each product link
            for product_url in product_links:
                page.goto(product_url)
                page.wait_for_load_state('load')

                product_html = page.content()
                product_soup = BeautifulSoup(product_html, 'html.parser')

                # Extract title (first h2 tag)
                title_element = product_soup.find("h2")
                title = title_element.get_text(strip=True) if title_element else "not found"

                # Remove "About " from the beginning of the title
                if title.lower().startswith("about "):
                    title = title[6:]  # Remove the first 6 characters ("About ")

                # Extract content (all h2 and p elements)
                content_elements = product_soup.find_all(["h2", "p"])
                content = "\n".join(elem.get_text(strip=True) for elem in content_elements if elem)

                # Extract important content (first 500 characters of content)
                important_content = content[:500] if content else ""

                # Extract images (all img tags)
                image_elements = product_soup.find_all("img")
                logos = [img.get("src") for img in image_elements if img.get("src")]


                dump_link_element = product_soup.find("a", class_="download-button")
                dumplink = dump_link_element["href"] if dump_link_element else "not found"

                # Store extracted data
                card_data = card_extraction_model(
                    m_company_name=title,  # Updated title without "About "
                    m_title=title,
                    m_url=product_url,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_base_url=self.base_url,
                    m_content=content,
                    m_important_content=important_content,
                    m_content_type="leaks",
                    m_email_addresses=helper_method.extract_emails(content) if content else [],
                    m_phone_numbers=helper_method.extract_phone_numbers(content) if content else [],
                    m_logo_or_images=logos,
                    m_dumplink=dumplink  # Added the dump link
                )

                self._card_data.append(card_data)

        except Exception as ex:
            print(f"An error occurred: {ex}")
