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

        page.wait_for_selector("h2", timeout=60000)  # waits up to 60 seconds

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        card_links = []
        h2_tags = soup.find_all("h2")
        print(f"Found {len(h2_tags)} <h2> tags.")

        for h2 in h2_tags:
            a_tag = h2.find("a")
            if a_tag and a_tag.get("href"):
                href = a_tag.get("href")
                # Use urljoin to join base_url and href correctly
                full_url = urljoin(self.base_url, href)
                print(f"Found card link: {full_url}")
                card_links.append(full_url)
        print(card_links)

        for link in card_links:
            page.goto(link, timeout=60000)
            html = page.content()
            self.soup = BeautifulSoup(html, "html.parser")

            m_content = ""
            dump_links = []
            page_title = page.title()
            page_url = page.url

            company_name = ""
            office_website = ""
            country = ""
            weblink = []

            industry = ""
            file_size = ""
            date = ""

            article_content = self.soup.find("div", class_="article-content")
            if article_content:

                company_name_tag = article_content.find("p")
                if company_name_tag:
                    content_text = company_name_tag.get_text(separator="\n", strip=True)
                    lines = content_text.split("\n")
                    for line in lines:
                        if "Name:" in line:
                            company_name = line.replace("Name:", "").strip()
                        elif "Office Website:" in line:
                            link_tag = company_name_tag.find("a")
                            office_website = link_tag.get("href") if link_tag else ""
                            if office_website:
                                weblink.append(office_website)
                        elif "Country:" in line:
                            country = line.replace("Country:", "").strip()
                        elif "Industry:" in line:
                            industry = line.replace("Industry:", "").strip()
                        elif "File Size:" in line:
                            file_size = line.replace("File Size:", "").strip()

                info_disclosure_section = article_content.find("h1", string="Information disclosure process")
                if info_disclosure_section:
                    ul_tag = info_disclosure_section.find_next("ul")
                    if ul_tag:
                        date_items = ul_tag.find_all("li")
                        if date_items:
                            date_text = date_items[0].get_text()
                            date = date_text.split()[0] if date_text else ""

                        m_content += "\nInformation disclosure process:\n"
                        for item in date_items:
                            m_content += "- " + item.get_text(strip=True) + "\n"

                files_section = article_content.find("h1", string="What files did we get")
                if files_section:
                    files_ul = files_section.find_next("ul")
                    if files_ul:
                        m_content += "\nWhat files did we get:\n"
                        for li in files_ul.find_all("li"):
                            m_content += "- " + li.get_text(strip=True) + "\n"

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
                            elif "https://mega.nz" in li.get_text():
                                dump_links.append(li.get_text(strip=True))

            card_data = leak_model(
                m_title=page_title,
                m_url=page_url,
                m_base_url=self.base_url,
                m_screenshot="",
                m_content=m_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=m_content,
                m_weblink=[],
                m_dumplink=dump_links,
                m_content_type=["leaks"],
                m_data_size=file_size,
                m_weblinks=weblink if weblink else [],

            )

            entity_data = entity_model(
                m_email=helper_method.extract_emails(m_content),
                m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                m_company_name=company_name,
                m_industry=industry,
                m_country_name=country
            )

            self.append_leak_data(card_data, entity_data)
