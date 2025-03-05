from abc import ABC
from datetime import datetime
import re

from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from urllib.parse import urljoin

from crawler.crawler_services.shared.helper_method import helper_method


class _rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion/index.html"

    @property
    def base_url(self) -> str:
        return "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion"

    def safe_find(self, page, selector, attr=None):
        try:
            element = page.query_selector(selector)
            if element:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None



    def parse_leak_data(self, page: Page):
        try:
            all_leak_urls = []
            base_domain = "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion"

            # Handle all pages from index.html through index7.html
            for page_num in range(1, 8):
                # Construct the URL based on page number
                if page_num == 1:
                    current_url = f"{base_domain}/index.html"
                else:
                    current_url = f"{base_domain}/index{page_num}.html"

                print(f"Processing page: {current_url}")

                # Navigate to current page
                page.goto(current_url)
                page.wait_for_load_state('load')

                # Get the HTML content of the page
                page_html = page.content()
                self.soup = BeautifulSoup(page_html, 'html.parser')

                # Find all list items within the ordered list
                list_items = self.soup.select("ol li")
                if not list_items:
                    print(f"No list items found on page: {current_url}")
                    continue

                # Extract leak URLs from each list item
                for item in list_items:
                    # Extract href from <a> tags within h4 tags
                    link_element = item.select_one("h4 b a")

                    if link_element and link_element.get('href'):
                        item_url = link_element.get('href')
                        if not item_url.startswith(('http://', 'https://')):
                            item_url = urljoin(base_domain, item_url)
                        all_leak_urls.append(item_url)

                        # Extract company name from <a> tags within h4 tags
                        title = link_element.get_text(strip=True)

                        # Extract description from <p> tags within <i> tags
                        desc_element = item.select_one("i p")
                        description = desc_element.get_text(strip=True) if desc_element else None

                        # Extract date
                        date_text = None
                        date_label = item.find("b", text="Date: ")
                        if date_label:
                            date_text = date_label.next_sibling.strip() if date_label.next_sibling else None

                        # Extract leak size from description
                        leak_size = None
                        if description:
                            size_match = re.search(r'Leak size: ([\d.]+\s*[KMGT]B)', description)
                            if size_match:
                                leak_size = size_match.group(1)

                        # Extract tags
                        tags = []
                        tag_elements = item.select("em b span a")
                        for tag in tag_elements:
                            tag_text = tag.get_text(strip=True)
                            if tag_text.startswith('#'):
                                tags.append(tag_text[1:])  # Remove the # symbol

                        # Create card data
                        card_data = card_extraction_model(
                            m_company_name=title,
                            m_title=title,
                            m_url=item_url,
                            m_weblink=[],
                            # m_dumplink=None,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_base_url=self.base_url,
                            m_content=description,
                            m_important_content=description,
                            m_logo_or_images=[],
                            m_content_type="leaks",
                            m_data_size=leak_size,
                            m_email_addresses=helper_method.extract_emails(description) if description else [],
                            m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                            m_leak_date=date_text,
                            # m_tags=tags
                        )

                        self._card_data.append(card_data)

            return all_leak_urls

        except Exception as ex:
            print(f"An error occurred: {ex}")
            return []