"""
Scrapy Middlewares for EdilEngine project.

Custom middlewares for user agent rotation, retry logic, and request handling.
"""

import logging
import time
from typing import Optional

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware as ScrapyRetryMiddleware
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object
from scrapy.utils.python import global_object_name

logger = logging.getLogger(__name__)


class UserAgentMiddleware:
    """
    Middleware for rotating user agents to avoid detection.
    
    Uses a list of common browser user agents and rotates them
    for each request to appear as different browsers.
    """
    
    USER_AGENTS = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    def __init__(self, user_agents: Optional[list[str]] = None):
        """Initialize with custom or default user agents."""
        self.user_agents = user_agents or self.USER_AGENTS
        self._index = 0
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler settings."""
        settings = crawler.settings
        user_agents = settings.getlist("USER_AGENT_LIST")
        if not user_agents:
            user_agents = None
        return cls(user_agents)
    
    def process_request(self, request: Request, spider: Spider) -> None:
        """Set a rotating user agent for each request."""
        user_agent = self.user_agents[self._index % len(self.user_agents)]
        self._index += 1
        request.headers.setdefault("User-Agent", user_agent)
        logger.debug(f"Set User-Agent: {user_agent[:50]}...")


class RetryMiddleware(ScrapyRetryMiddleware):
    """
    Custom retry middleware with exponential backoff.
    
    Implements exponential backoff for retries to avoid overwhelming
    target servers and to handle rate limiting gracefully.
    """
    
    def __init__(self, settings):
        """Initialize retry middleware with settings."""
        super().__init__(settings)
        self.max_delay = settings.getint("AUTOTHROTTLE_MAX_DELAY", 60)
    
    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Request | Response:
        """Process response and retry if necessary with exponential backoff."""
        if request.meta.get("dont_retry", False):
            return response
        
        if response.status in self.retry_http_codes:
            reason = response.status
            return self._retry(request, reason, spider) or response
        
        return response
    
    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ) -> Request | None:
        """Process exceptions and retry with exponential backoff."""
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get(
            "dont_retry", False
        ):
            return self._retry(request, exception, spider)
        return None
    
    def _retry(
        self, request: Request, reason: str | Exception, spider: Spider
    ) -> Request | None:
        """Retry request with exponential backoff."""
        retries = request.meta.get("retry_times", 0) + 1
        
        if retries <= self.max_retry_times:
            logger.debug(
                f"Retrying {request.url} (failed {retries} times): {reason}",
                extra={"spider": spider},
            )
            
            # Calculate exponential backoff delay
            base_delay = self.settings.getint("DOWNLOAD_DELAY", 1)
            delay = min(base_delay * (2 ** (retries - 1)), self.max_delay)
            
            new_request = request.copy()
            new_request.meta["retry_times"] = retries
            new_request.dont_filter = True
            new_request.priority = request.priority - self.priority_adjust
            
            # Schedule retry with delay
            spider.crawler.engine.crawl(new_request, delay=delay)
            return None
        
        logger.debug(
            f"Gave up retrying {request.url} (failed {retries} times): {reason}",
            extra={"spider": spider},
        )
        return None


class EdilengineSpiderMiddleware:
    """
    Spider middleware for EdilEngine project.
    
    Provides hooks for processing spider input/output.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_spider_input(self, response: Response, spider: Spider):
        """Process incoming response before it reaches the spider."""
        logger.debug(f"Processing response from {response.url}")
        return None

    def process_spider_output(self, response: Response, result, spider: Spider):
        """Process output from spider."""
        for item in result:
            yield item

    def process_spider_exception(
        self, response: Response, exception: Exception, spider: Spider
    ):
        """Handle exceptions raised during spider processing."""
        logger.error(
            f"Exception in spider {spider.name} processing {response.url}: {exception}",
            exc_info=True,
        )
        return None

    def process_start_requests(self, start_requests, spider: Spider):
        """Process start requests."""
        for request in start_requests:
            yield request

    def spider_opened(self, spider: Spider):
        """Called when spider opens."""
        logger.info(f"Spider opened: {spider.name}")

    def spider_closed(self, spider: Spider, reason: str):
        """Called when spider closes."""
        logger.info(f"Spider closed: {spider.name}, reason: {reason}")


class EdilengineDownloaderMiddleware:
    """
    Downloader middleware for EdilEngine project.
    
    Provides hooks for processing requests and responses.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request: Request, spider: Spider):
        """Process outgoing request."""
        logger.debug(f"Request: {request.method} {request.url}")
        return None

    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Response:
        """Process incoming response."""
        logger.debug(f"Response: {response.status} {response.url}")
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ):
        """Handle download exceptions."""
        logger.warning(f"Download exception for {request.url}: {exception}")
        return None

    def spider_opened(self, spider: Spider):
        """Called when spider opens."""
        logger.info(f"Downloader middleware initialized for: {spider.name}")
