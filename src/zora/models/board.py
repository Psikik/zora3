"""BoardState domain model — the structured output of a board read."""

from dataclasses import dataclass, field

from zora.models.assignment import Assignment
from zora.models.ship import Ship


@dataclass
class BoardState:
    """Aggregated state read from the admiralty board.

    This is the top-level structured output the spec requires: all
    assignments and ships visible on the current board view.
    """

    assignments: list[Assignment] = field(default_factory=list)
    ships: list[Ship] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON output."""
        result = {
            "assignments": [a.to_dict() for a in self.assignments],
            "ships": [s.to_dict() for s in self.ships],
        }
        if self.errors:
            result["errors"] = self.errors
        return result
