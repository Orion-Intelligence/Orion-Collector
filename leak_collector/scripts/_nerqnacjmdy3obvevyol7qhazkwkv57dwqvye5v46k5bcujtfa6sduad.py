import datetime
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


class _nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad(leak_extractor_interface, ABC):
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
            cls._instance = super(_nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad.onion"

    @property
    def base_url(self) -> str:
        return "http://nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_resoource_block=False, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:

        return "https://www.iana.org/help/example-domains"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        current_page = 1
        max_pages = 20
        base_pagination_url = f"{self.base_url}/?PAGEN_1="
        processed_urls = set()

        while current_page <= max_pages:
            try:
                target_url = self.base_url if current_page == 1 else f"{base_pagination_url}{current_page}"
                page.goto(target_url, timeout=180000, wait_until="networkidle")
                print(f"Loaded page {current_page}: {target_url}")

                detail_urls = []
                card_links = page.locator("a[href*='code=']").all()

                for link in card_links:
                    try:
                        # Skip <a> tags with class="title" or inside an element with class="title"
                        if link.locator(
                                ":scope.title, :scope.date, :scope >> xpath=ancestor::*[contains(@class, 'title') or contains(@class, 'date') or contains(@class, 'inner')]"
                        ).count() > 0:
                            continue

                        detail_href = link.get_attribute("href")
                        if not detail_href or 'code=' not in detail_href:
                            continue

                        if detail_href.startswith('http'):
                            detail_url = detail_href
                        else:
                            detail_url = f"{self.base_url.rstrip('/')}/{detail_href.lstrip('/')}"

                        detail_url = detail_url.replace('detail?code=', 'detail/?code=')

                        if not detail_url.startswith(f"{self.base_url}/detail/?code="):
                            continue

                        if detail_url not in processed_urls:
                            detail_urls.append(detail_url)
                            processed_urls.add(detail_url)
                            print(f"Collected URL: {detail_url}")

                    except Exception as e:
                        print(f"Error collecting URL: {str(e)}")
                        continue

                if not detail_urls:
                    print(f"No valid URLs found on page {current_page}")
                    current_page += 1
                    continue

                for detail_url in detail_urls:
                    try:
                        print(f"Processing: {detail_url}")
                        page.goto(detail_url, timeout=180000, wait_until="networkidle")

                        if not page.url.startswith(f"{self.base_url}/detail/?code="):
                            print(f"Navigation mismatch: expected {detail_url}, got {page.url}")
                            continue

                        # Get all text excluding .title elements
                        full_text = page.locator("body").evaluate("""
                            (body) => {
                                // Remove all <img> tags
                                body.querySelectorAll('img').forEach(el => el.remove());

                                // Remove elements with class 'title' or 'date'
                                body.querySelectorAll('.title, .date, .inner').forEach(el => el.remove());

                                // Track all .listing elements that come after any <h2>
                                const h2Elements = Array.from(body.querySelectorAll('h2'));
                                const listingElements = Array.from(body.querySelectorAll('.listing'));
                                
                                listingElements.forEach(listing => {
                                    for (let h2 of h2Elements) {
                                        if (h2.compareDocumentPosition(listing) & Node.DOCUMENT_POSITION_FOLLOWING) {
                                            listing.remove();
                                            break; // Remove only once per h2
                                        }
                                    }
                                    
                                });

                                return body.innerText;
                            }
                        """)

                        title = page.locator("h1").first.text_content(timeout=10000)

                        leak_date = None
                        date_element = page.locator("time, span.date").first
                        if date_element.count() > 0:
                            try:
                                date_str = date_element.text_content()
                                leak_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
                            except Exception as date_error:
                                print(f"Date parsing error: {date_error}")

                        websites = list(set(
                            helper_method.extract_websites(full_text) +
                            [a.get_attribute("href") for a in page.locator("a[href^='http']").all()
                             if a.get_attribute("href")]
                        ))

                        images = [
                            img.get_attribute("src")
                            for img in page.locator("img").all()
                            if img.get_attribute("src")
                               and img.get_attribute("src").startswith("http")
                               and not img.get_attribute("title")
                               and not img.get_attribute("alt")
                        ]

                        leak = leak_model(
                            m_title=title,
                            m_url=detail_url,
                            m_base_url=self.base_url,
                            m_content=full_text,
                            m_important_content=full_text[:500],
                            m_network=helper_method.get_network_type(self.base_url),
                            m_section=["leak"],
                            m_content_type=["leaks"],
                            m_screenshot=helper_method.get_screenshot_base64(page, title),
                            m_weblink=websites,
                            m_dumplink=[],
                            m_websites=websites,
                            m_logo_or_images=images,
                            m_leak_date=leak_date
                        )

                        entity = entity_model(
                            m_phone_numbers=helper_method.extract_phone_numbers(full_text),
                            m_company_name=title,
                            m_ip=[self.base_url],
                            m_team="public"
                        )

                        self.append_leak_data(leak, entity)
                        print(f"Successfully processed: {detail_url}")

                    except Exception as card_error:
                        print(f"Error processing {detail_url}: {str(card_error)}")
                        continue

                print(f"Completed page {current_page}")
                current_page += 1

            except Exception as page_error:
                print(f"Error loading page {current_page}: {str(page_error)}")
                current_page += 1

        print(f"Finished processing all pages. Total URLs processed: {len(processed_urls)}")

