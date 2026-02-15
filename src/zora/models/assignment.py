"""Assignment domain model."""

from dataclasses import dataclass, field


@dataclass
class Assignment:
    """An admiralty mission with stat requirements and ship slots.

    Represents one assignment card from the admiralty board. Fields match
    what the spec requires for milestone 1: name, stats, ship slots,
    duration, rarity, and event rewards.
    """

    name: str
    engineering: int
    science: int
    tactical: int
    ship_slots: int
    campaign: str = ""
    duration: str = ""
    rarity: str = ""
    event_rewards: list[str] = field(default_factory=list)

    def total_required(self) -> int:
        """Return the sum of all three required stat values."""
        return self.engineering + self.science + self.tactical

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON output."""
        return {
            "name": self.name,
            "engineering": self.engineering,
            "science": self.science,
            "tactical": self.tactical,
            "ship_slots": self.ship_slots,
            "campaign": self.campaign,
            "duration": self.duration,
            "rarity": self.rarity,
            "event_rewards": self.event_rewards,
        }
