"""Ship domain model."""

from dataclasses import dataclass, field


@dataclass
class Ship:
    """A ship card with Engineering, Science, and Tactical stats.

    Ships go on maintenance (cooldown) after being assigned to a mission.
    """

    name: str
    engineering: int
    science: int
    tactical: int
    maintenance: bool = False
    special_abilities: list[str] = field(default_factory=list)

    def total_stats(self) -> int:
        """Return the sum of all three stat values."""
        return self.engineering + self.science + self.tactical

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON output."""
        return {
            "name": self.name,
            "engineering": self.engineering,
            "science": self.science,
            "tactical": self.tactical,
            "maintenance": self.maintenance,
            "special_abilities": self.special_abilities,
        }
