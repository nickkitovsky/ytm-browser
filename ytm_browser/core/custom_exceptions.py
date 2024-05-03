"""Exceptions module."""


class TooManyRetryError(Exception):
    """TooManyRetryError exception class for retry decorator."""


class ExistingClientNotFoundError(Exception):
    """Api client not found."""


class PayloadError(Exception):
    """Wrong payload format."""


class CredentialsFilesError(Exception):
    """Parse authfile error."""


class CredentialsDataError(Exception):
    """Error loading authdata."""


class DumpAuthFileError(Exception):
    """Curl file content not found."""


class ParsingError(Exception):
    """Error of parsing data."""


class ParserError(Exception):
    """Error of initialize parser."""


class FetchResponseError(Exception):
    """Error of fetch resonse."""


class ChainError(Exception):
    """Error of fetch resonse."""


class ResponseError(Exception):
    """Error of fetch resonse."""
