import os.path
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class MatcherOptions:
    """
    Options for checking against a list of exclude/include patterns.

    :param source: File name to read exclusion rules from.
    :param extension: Extension to narrow down search to.
    """

    source: str
    extension: Optional[str] = None

    def __post_init__(self) -> None:
        if self.extension is not None and not self.extension.startswith("."):
            self.extension = f".{self.extension}"


class Matcher:
    "Compares file and directory names against a list of exclude/include patterns."

    options: MatcherOptions
    rules: List[str]

    def __init__(self, options: MatcherOptions, directory: Path) -> None:
        self.options = options
        if os.path.exists(directory / options.source):
            with open(directory / options.source, "r") as f:
                rules = f.read().splitlines()
            self.rules = [rule for rule in rules if rule and not rule.startswith("#")]
        else:
            self.rules = []

    def extension_matches(self, name: str) -> bool:
        "True if the file name has the expected extension."

        return self.options.extension is None or name.endswith(self.options.extension)

    def is_excluded(self, name: str) -> bool:
        "True if the file or directory name matches any of the exclusion patterns."

        if name.startswith("."):
            return True

        if not self.extension_matches(name):
            return True

        for rule in self.rules:
            if fnmatch(name, rule):
                return True
        else:
            return False

    def is_included(self, name: str) -> bool:
        "True if the file or directory name matches none of the exclusion patterns."

        return not self.is_excluded(name)

    def filter(self, items: Iterable[str]) -> List[str]:
        """
        Returns only those elements from the input that don't match any of the exclusion rules.

        :param items: A list of names to filter.
        :returns: A filtered list of names that didn't match any of the exclusion rules.
        """

        return [item for item in items if self.is_included(item)]

    def scandir(self, path: Path) -> List[str]:
        """
        Returns only those entries in a directory whose name doesn't match any of the exclusion rules.

        :param path: Directory to scan.
        :returns: A filtered list of entries whose name didn't match any of the exclusion rules.
        """

        return self.filter(entry.name for entry in os.scandir(path))