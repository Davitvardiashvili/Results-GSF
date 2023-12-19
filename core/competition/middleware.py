import logging

logger = logging.getLogger(__name__)

class RequestBodyLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the incoming request body
        logger.info(f"Incoming Request Body: {request.body}")

        response = self.get_response(request)
        return response