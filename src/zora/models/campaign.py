"""Campaign domain model."""

from dataclasses import dataclass


@dataclass
class Campaign:
    """An admiralty track (Klingon, Ferengi, Romulan, etc.).

    The campaign is user-selected, not extracted from assignment cards.
    """

    name: str

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON output."""
        return {
            "name": self.name,
        }
