"""Tests for domain models."""

from zora.models import Assignment, BoardState, Campaign, Ship


class TestShip:
    def test_construction_minimal(self) -> None:
        ship = Ship(name="USS Enterprise", engineering=50, science=30, tactical=40)
        assert ship.name == "USS Enterprise"
        assert ship.engineering == 50
        assert ship.science == 30
        assert ship.tactical == 40
        assert ship.maintenance is False
        assert ship.special_abilities == []

    def test_construction_full(self) -> None:
        ship = Ship(
            name="USS Defiant",
            engineering=20,
            science=10,
            tactical=80,
            maintenance=True,
            special_abilities=["+10 TAC against Klingon"],
        )
        assert ship.maintenance is True
        assert ship.special_abilities == ["+10 TAC against Klingon"]

    def test_total_stats(self) -> None:
        ship = Ship(name="Test", engineering=10, science=20, tactical=30)
        assert ship.total_stats() == 60

    def test_to_dict(self) -> None:
        ship = Ship(name="USS Voyager", engineering=40, science=60, tactical=20)
        d = ship.to_dict()
        assert d == {
            "name": "USS Voyager",
            "engineering": 40,
            "science": 60,
            "tactical": 20,
            "maintenance": False,
            "special_abilities": [],
        }

    def test_special_abilities_default_not_shared(self) -> None:
        """Each Ship instance gets its own list for special_abilities."""
        ship_a = Ship(name="A", engineering=0, science=0, tactical=0)
        ship_b = Ship(name="B", engineering=0, science=0, tactical=0)
        ship_a.special_abilities.append("test")
        assert ship_b.special_abilities == []


class TestAssignment:
    def test_construction_minimal(self) -> None:
        a = Assignment(
            name="Patrol Sector",
            engineering=30,
            science=20,
            tactical=10,
            ship_slots=2,
        )
        assert a.name == "Patrol Sector"
        assert a.engineering == 30
        assert a.science == 20
        assert a.tactical == 10
        assert a.ship_slots == 2
        assert a.campaign == ""
        assert a.duration == ""
        assert a.rarity == ""
        assert a.event_rewards == []

    def test_construction_full(self) -> None:
        a = Assignment(
            name="Rescue Mission",
            engineering=50,
            science=40,
            tactical=30,
            ship_slots=3,
            campaign="Klingon",
            duration="4h",
            rarity="Rare",
            event_rewards=["Dilithium x100"],
        )
        assert a.campaign == "Klingon"
        assert a.duration == "4h"
        assert a.rarity == "Rare"
        assert a.event_rewards == ["Dilithium x100"]

    def test_total_required(self) -> None:
        a = Assignment(
            name="Test", engineering=10, science=20, tactical=30, ship_slots=1
        )
        assert a.total_required() == 60

    def test_to_dict(self) -> None:
        a = Assignment(
            name="Supply Run",
            engineering=15,
            science=5,
            tactical=25,
            ship_slots=2,
            campaign="Ferengi",
            duration="2h",
            rarity="Common",
            event_rewards=[],
        )
        d = a.to_dict()
        assert d["name"] == "Supply Run"
        assert d["ship_slots"] == 2
        assert d["campaign"] == "Ferengi"
        assert d["duration"] == "2h"
        assert d["rarity"] == "Common"

    def test_event_rewards_default_not_shared(self) -> None:
        """Each Assignment instance gets its own list for event_rewards."""
        a1 = Assignment(name="A", engineering=0, science=0, tactical=0, ship_slots=1)
        a2 = Assignment(name="B", engineering=0, science=0, tactical=0, ship_slots=1)
        a1.event_rewards.append("reward")
        assert a2.event_rewards == []


class TestCampaign:
    def test_construction(self) -> None:
        c = Campaign(name="Klingon")
        assert c.name == "Klingon"

    def test_to_dict(self) -> None:
        c = Campaign(name="Romulan")
        assert c.to_dict() == {"name": "Romulan"}


class TestBoardState:
    def test_empty_board(self) -> None:
        board = BoardState()
        assert board.assignments == []
        assert board.ships == []

    def test_board_with_data(self) -> None:
        ship = Ship(name="Enterprise", engineering=50, science=30, tactical=40)
        assignment = Assignment(
            name="Patrol", engineering=20, science=10, tactical=15, ship_slots=2
        )
        board = BoardState(assignments=[assignment], ships=[ship])
        assert len(board.assignments) == 1
        assert len(board.ships) == 1

    def test_to_dict(self) -> None:
        ship = Ship(name="Enterprise", engineering=50, science=30, tactical=40)
        assignment = Assignment(
            name="Patrol", engineering=20, science=10, tactical=15, ship_slots=2
        )
        board = BoardState(assignments=[assignment], ships=[ship])
        d = board.to_dict()
        assert len(d["assignments"]) == 1
        assert len(d["ships"]) == 1
        assert d["assignments"][0]["name"] == "Patrol"
        assert d["ships"][0]["name"] == "Enterprise"

    def test_to_dict_empty(self) -> None:
        board = BoardState()
        d = board.to_dict()
        assert d == {"assignments": [], "ships": []}

    def test_lists_default_not_shared(self) -> None:
        """Each BoardState instance gets its own lists."""
        b1 = BoardState()
        b2 = BoardState()
        b1.assignments.append(
            Assignment(name="X", engineering=0, science=0, tactical=0, ship_slots=1)
        )
        assert b2.assignments == []


class TestModelImports:
    """Verify re-exports from zora.models work."""

    def test_import_from_package(self) -> None:
        from zora.models import Assignment, BoardState, Campaign, Ship

        assert Ship is not None
        assert Assignment is not None
        assert Campaign is not None
        assert BoardState is not None
