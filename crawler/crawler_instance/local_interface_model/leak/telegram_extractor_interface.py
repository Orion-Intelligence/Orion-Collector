from abc import ABC, abstractmethod
from typing import List

from playwright.async_api import Page

from crawler.crawler_instance.local_interface_model.leak.model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel
from crawler.crawler_services.redis_manager.redis_enums import CUSTOM_SCRIPT_REDIS_KEYS


class telegram_extractor_interface(ABC):
    @abstractmethod
    def parse_leak_data(self, page: Page) -> leak_data_model:
        """Parse leak data from the given Playwright page and return a leak_data_model."""
        pass

    @property
    @abstractmethod
    def seed_url(self) -> str:
        """Return the seed URL to start crawling from."""
        pass

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Return the name of the Telegram channel."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base domain URL of the source."""
        pass

    @property
    @abstractmethod
    def rule_config(self) -> RuleModel:
        """Return the crawling rule configuration."""
        pass

    @property
    @abstractmethod
    def card_data(self) -> List[telegram_chat_model]:
        """Return the list of parsed leak models (card data)."""
        pass

    @property
    @abstractmethod
    def entity_data(self) -> List[entity_model]:
        """Return the list of parsed leak models (entity data)."""
        pass

    @abstractmethod
    def contact_page(self) -> str:
        """Return the contact page URL of the data source."""
        pass

    @abstractmethod
    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, value):
        """Interact with Redis using the given command, key, and value."""
        pass

    @abstractmethod
    def append_leak_data(self, leak: telegram_chat_model):
        """Append a single leak_model instance to the collected card data."""
        pass

    def init_callback(self, callback):
        """pass callback model triggered on leak parsed"""
        pass
