from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.shared.helper_method import helper_method
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
class _direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd(leak_extractor_interface, ABC):
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
            cls._instance = super(_direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd.onion/"

    @property
    def base_url(self) -> str:
        return "http://direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd.onion/"

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
        return "http://direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd.onion/contact.html"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):

        page.wait_for_selector("h2", timeout=60000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        cards_info = []
        for article_content in soup.find_all("div", class_="article-content"):
            h2 = article_content.find("h2")
            desc_tag = article_content.find("p")
            a_tag = h2.find("a") if h2 else None
            if a_tag and a_tag.get("href"):
                href = a_tag.get("href")
                full_url = urljoin(self.base_url, href)
                description = desc_tag.get_text(strip=True) if desc_tag else ""
                cards_info.append({
                    "href": full_url,
                    "description": description
                })

        for card in cards_info:
            link = card["href"]
            description_text = card["description"]
            page.goto(link, timeout=60000)
            html = page.content()
            self.soup = BeautifulSoup(html, "html.parser")
            m_content = ""
            dump_links = []

            company_name = ""
            country = ""
            website = []
            industry = ""
            file_size = ""
            date_only = ""

            article_content = self.soup.find("div", class_="article-content")
            if article_content:
                company_info_tag = article_content.find("p")
                if company_info_tag:
                    for strong_tag in company_info_tag.find_all("strong"):
                        label = strong_tag.get_text(strip=True)
                        if label == "Name:":
                            company_name = strong_tag.next_sibling.strip()
                        elif label == "Office Website:":
                            link_tag = strong_tag.find_next("a")
                            if link_tag:
                                office_website = link_tag.get_text(strip=True)
                                website.append(office_website)
                        elif label == "Country:":
                            country = strong_tag.next_sibling.strip()
                        elif label == "Industry:":
                            industry = strong_tag.next_sibling.strip()
                        elif label == "File Size:":
                            file_size = strong_tag.next_sibling.strip()

                import re

                info_disclosure_section = article_content.find("h1", string="Information disclosure process")
                if info_disclosure_section:
                    ul_tag = info_disclosure_section.find_next("ul")
                    if ul_tag:
                        date_items = ul_tag.find_all("li")
                        if date_items:
                            for idx, item in enumerate(date_items):
                                raw_text = item.get_text(strip=True)

                                match = re.search(r"\d{4}/\d{1,2}/\d{1,2}", raw_text)
                                if match:
                                    date_only = match.group()
                                else:
                                    print(f"No valid date found at index {idx}")

                        info_items = [item.get_text(strip=True) for item in date_items]
                        m_content += "Information disclosure process: " + ', '.join(info_items)

                files_section = article_content.find("h1", string="What files did we get")
                if files_section:
                    files_ul = files_section.find_next("ul")
                    if files_ul:
                        m_content += "\nWhat files did we get:\n"
                        for li in files_ul.find_all("li"):
                            m_content += "- " + li.get_text(strip=True)



                address_section = article_content.find("h1", string="Information disclosure address")
                if address_section:
                    address_ul = address_section.find_next("ul")
                    if address_ul:
                        for li in address_ul.find_all("li"):
                            link = li.find("a")
                            if link and link.get("href"):
                                href = link.get("href")
                                if href.startswith("/"):
                                    href = self.base_url.rstrip("/") + href
                                dump_links.append(href)

                            text_content = li.get_text(strip=True)
                            urls_in_text = re.findall(r'(https?://[^\s<>"]+)', text_content)
                            for url in urls_in_text:
                                if url not in dump_links:
                                    dump_links.append(url)

            card_data = leak_model(
                m_title=page.title(),
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot="",
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=description_text,
                m_dumplink=dump_links,
                m_content_type=["leaks"],
                m_data_size=file_size,
                m_weblink=website if website else [],
                m_leak_date=helper_method.extract_and_convert_date(date_only)

            )

            entity_data = entity_model(
                m_email=helper_method.extract_emails(m_content),
                m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                m_company_name=company_name,
                m_industry=industry,
                m_country_name=country
            )

            self.append_leak_data(card_data, entity_data)
