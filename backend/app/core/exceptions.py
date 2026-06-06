from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, 422)


class ProviderRateLimitError(AppException):
    def __init__(self, provider: str):
        super().__init__(f"Rate limit hit for provider: {provider}", 429)


class ProviderError(AppException):
    def __init__(self, provider: str, detail: str = ""):
        super().__init__(f"Provider {provider} failed: {detail}", 502)


class AllProvidersExhaustedError(AppException):
    def __init__(self):
        super().__init__("All AI providers failed or rate limited", 503)


class GenerationFailedError(AppException):
    def __init__(self, detail: str = ""):
        super().__init__(f"Content generation failed: {detail}", 500)


class DailyLimitExceededError(AppException):
    def __init__(self):
        super().__init__("Daily generation limit exceeded", 429)


def raise_http(exc: AppException) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
