from abc import ABC
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from trio import fail_after

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _monitor_mozilla(leak_extractor_interface, ABC):
  _instance = None

  def __init__(self):
    self._card_data = []
    self.soup = None
    self._initialized = None
    self._redis_instance = redis_controller()

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(_monitor_mozilla, cls).__new__(cls)
      cls._instance._initialized = False
    return cls._instance

  @property
  def seed_url(self) -> str:
    return "https://monitor.mozilla.org/breaches"

  @property
  def base_url(self) -> str:
    return "https://monitor.mozilla.org/breaches"

  @property
  def rule_config(self) -> RuleModel:
    return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

  @property
  def card_data(self) -> List[leak_model]:
    return self._card_data

  def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
    return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

  def contact_page(self) -> str:
    return "https://support.mozilla.org"

  def parse_leak_data(self, page: Page):
    page.wait_for_load_state("domcontentloaded")
    breach_cards = page.locator('a[class^="BreachIndexView_breachCard"]')
    breach_cards.first.wait_for(state="visible")
    card_count = breach_cards.count()

    self._card_data = []
    error_count = 0
    max_errors = 20

    card_list = []
    for i in range(card_count):
      try:
        card = page.locator('a[class^="BreachIndexView_breachCard"]').nth(i)
        card.wait_for(state="visible")

        card_content = helper_method.clean_text(card.inner_text())
        card_href = card.get_attribute('href')
        card_title = helper_method.clean_text(card.locator('h2').inner_text())
        base = "https://monitor.mozilla.org" +"/"+card_href

        card_list.append({
          'content': card_content,
          'href': card_href,
          'title': card_title,
          'dumplink': base
        })

      except Exception as ex:
        error_count += 1
        print(f"Error collecting card {i}: {ex}")
        if error_count >= max_errors:
          break
        continue

    for card_data in card_list:
      if error_count >= max_errors:
        break

      try:
        page.goto(card_data['dumplink'])
        page.wait_for_load_state("domcontentloaded")

        soup = BeautifulSoup(page.content(), "html.parser")
        extracted_text = helper_method.clean_text(soup.get_text(separator=" ", strip=True))
        current_url = page.url

        leak_data = leak_model(
          m_title=card_data['title'],
          m_url=current_url,
          m_base_url=self.base_url,
          m_content=extracted_text,
          m_network=helper_method.get_network_type(self.base_url),
          m_important_content=card_data['content'],
          m_weblink=[current_url],
          m_dumplink=[card_data['dumplink']],
          m_email_addresses=helper_method.extract_emails(extracted_text),
          m_phone_numbers=helper_method.extract_phone_numbers(extracted_text),
          m_content_type=["leaks"],
        )

        self._card_data.append(leak_data)
        error_count = 0

      except Exception as ex:
        error_count += 1
        continue
    return self._card_data