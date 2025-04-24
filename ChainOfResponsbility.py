"""
Request Processing System Using Chain of Responsibility Pattern
"""

import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Request:
    """
    Represents an incoming request with validation
    
    Attributes:
        request_id (str): Unique request identifier
        data (str): Sanitized request payload
        client_ip (str): Validated IP address
    """
    def __init__(self, request_id: str, data: str, client_ip: str):
        self.request_id = request_id
        self._data = data
        self._client_ip = client_ip

    @property
    def data(self) -> str:
        return self._data.strip() if self._data else ''

    @property
    def client_ip(self) -> str:
        return self._client_ip

class Handler(ABC):
    """Abstract base handler in the chain"""
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self.next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Request) -> str:
        pass

class DataValidationHandler(Handler):
    """Validates and sanitizes request data"""
    def handle(self, request: Request) -> str:
        if not request.data:
            logger.warning("Invalid data format")
            return "Rejected: Invalid data format"
        logger.info("Data validation passed")
        return super().handle(request) if self.next_handler else "Validation Complete"

class IPFilteringHandler(Handler):
    """Blocks requests from restricted IP addresses"""
    def __init__(self, blocked_ips: set = None):
        super().__init__()
        self.blocked_ips = blocked_ips or {"192.168.0.10", "10.0.0.1"}

    def handle(self, request: Request) -> str:
        if request.client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP: {request.client_ip}")
            return f"Rejected: Blocked IP {request.client_ip}"
        logger.info("IP check passed")
        return super().handle(request) if self.next_handler else "IP Check Complete"

class CachingHandler(Handler):
    """Caches frequent requests"""
    def __init__(self, cache: dict = None):
        super().__init__()
        self.cache = cache or {"123": "Cached Response for request 123"}

    def handle(self, request: Request) -> str:
        if cached_response := self.cache.get(request.request_id):
            logger.info(f"Cache hit: {request.request_id}")
            return cached_response
        logger.info("Cache miss")
        return super().handle(request) if self.next_handler else "Cache Check Complete"

class FinalProcessingHandler(Handler):
    """Executes core business logic"""
    def handle(self, request: Request) -> str:
        logger.info(f"Processing request {request.request_id}")
        return f"Processed: {request.request_id} with data '{request.data}'"

# Configuration
if __name__ == "__main__":
    # Create handler chain
    validation_handler = DataValidationHandler()
    ip_handler = IPFilteringHandler()
    cache_handler = CachingHandler()
    processing_handler = FinalProcessingHandler()

    validation_handler.set_next(ip_handler).set_next(cache_handler).set_next(processing_handler)

    # Test cases
    test_requests = [
        Request("200", "Order: 5 units", "192.168.1.5"),
        Request("201", "Order: 10 units", "192.168.0.10"),
        Request("123", "Cached content", "192.168.1.8")
    ]

    for req in test_requests:
        print(f"\nProcessing {req.request_id}:")
        print(validation_handler.handle(req))