import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from api.schemas import (
    BrandProfile,
    HistoryCreate,
    HistoryEntry,
    PlaybookEntry,
    TrackerEntry,
    TrackerEntryCreate,
    TrackerGoals,
)
from bot.settings import settings


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


class DataStore:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base = base_dir or settings.bot_data_dir
        self.base.mkdir(parents=True, exist_ok=True)

    @property
    def _brand_path(self) -> Path:
        return self.base / "brand.json"

    @property
    def _playbooks_path(self) -> Path:
        return self.base / "playbooks.json"

    @property
    def _history_path(self) -> Path:
        return self.base / "history.json"

    @property
    def _tracker_path(self) -> Path:
        return self.base / "tracker.json"

    def get_brand(self) -> BrandProfile:
        raw = _read_json(self._brand_path, {})
        return BrandProfile.model_validate(raw)

    def save_brand(self, brand: BrandProfile) -> BrandProfile:
        _write_json(self._brand_path, brand.model_dump())
        return brand

    def list_playbooks(self) -> List[PlaybookEntry]:
        raw = _read_json(self._playbooks_path, [])
        return [PlaybookEntry.model_validate(item) for item in raw]

    def get_playbook(self, subreddit: str) -> Optional[PlaybookEntry]:
        key = _normalize_subreddit(subreddit)
        for entry in self.list_playbooks():
            if _normalize_subreddit(entry.subreddit) == key:
                return entry
        return None

    def save_playbooks(self, playbooks: List[PlaybookEntry]) -> List[PlaybookEntry]:
        _write_json(self._playbooks_path, [p.model_dump() for p in playbooks])
        return playbooks

    def list_history(self) -> List[HistoryEntry]:
        raw = _read_json(self._history_path, [])
        return [HistoryEntry.model_validate(item) for item in raw]

    def add_history(self, data: HistoryCreate) -> HistoryEntry:
        entry = HistoryEntry(
            id=uuid.uuid4().hex[:12],
            created_at=_utc_now(),
            **data.model_dump(),
        )
        items = self.list_history()
        items.insert(0, entry)
        _write_json(self._history_path, [i.model_dump() for i in items])
        return entry

    def get_tracker_goals(self) -> TrackerGoals:
        raw = _read_json(self._tracker_path, {})
        goals = dict(raw.get("goals", {}))
        goals.pop("goal_installs", None)
        goals.setdefault("goal_upvotes", 100)
        return TrackerGoals.model_validate(goals)

    def save_tracker_goals(self, goals: TrackerGoals) -> TrackerGoals:
        raw = _read_json(self._tracker_path, {"goals": {}, "entries": []})
        raw["goals"] = goals.model_dump()
        _write_json(self._tracker_path, raw)
        return goals

    def list_tracker_entries(self) -> List[TrackerEntry]:
        raw = _read_json(self._tracker_path, {"goals": {}, "entries": []})
        entries = []
        for item in raw.get("entries", []):
            cleaned = {k: v for k, v in item.items() if k != "installs"}
            entries.append(TrackerEntry.model_validate(cleaned))
        return entries

    def add_tracker_entry(self, data: TrackerEntryCreate) -> TrackerEntry:
        entry = TrackerEntry(
            id=uuid.uuid4().hex[:12],
            created_at=_utc_now(),
            **data.model_dump(),
        )
        raw = _read_json(self._tracker_path, {"goals": {}, "entries": []})
        entries = raw.get("entries", [])
        entries.insert(0, entry.model_dump())
        raw["entries"] = entries
        _write_json(self._tracker_path, raw)
        return entry


def _normalize_subreddit(name: str) -> str:
    return name.lower().removeprefix("r/").removeprefix("/").strip()


def playbook_note(entry: PlaybookEntry) -> str:
    parts = []
    if entry.summary:
        parts.append(entry.summary)
    if entry.angles:
        parts.append("Angles: " + "; ".join(entry.angles))
    if entry.dos_donts:
        parts.append("Dos/donts: " + entry.dos_donts)
    return " ".join(parts)[:600]