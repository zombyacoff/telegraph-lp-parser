from dataclasses import dataclass

from ..constants.constants import (
    CONFIG_FILE_ERROR_MESSAGE,
    ERROR_TITLE,
    FILE_NOT_FOUND_TEXT,
    INCORRECT_OFFSET_TEXT,
    INCORRECT_RELEASE_DATE_TEXT,
    INCORRECT_WEBSITES_TEXT,
)
from ..extensions.utils import paint_text


class ApplicationException(Exception):
    """Base class for all application exceptions"""

    @staticmethod
    def get_error_message(exception: Exception) -> str:
        print(
            paint_text(ERROR_TITLE, 31, True),
            exception.message,
            sep="\n",
        )


class ConfigException(ApplicationException):
    """Base class for all config exceptions"""

    @property
    def message(self) -> str:
        return CONFIG_FILE_ERROR_MESSAGE


class ConfigNotFoundError(ConfigException):
    @property
    def message(self) -> str:
        return FILE_NOT_FOUND_TEXT


class IncorrectOffsetError(ConfigException):
    @property
    def message(self) -> str:
        return INCORRECT_OFFSET_TEXT


@dataclass
class IncorrectReleaseDateError(ConfigException):
    release_date: any

    @property
    def message(self) -> str:
        return INCORRECT_RELEASE_DATE_TEXT.format(release_date=self.release_date)


@dataclass
class IncorrectWebsitesError(ConfigException):
    url: any

    @property
    def message(self) -> str:
        return INCORRECT_WEBSITES_TEXT.format(url=self.url)
