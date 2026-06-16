from fastapi import APIRouter

from api.schemas import (
    TrackerEntry,
    TrackerEntryCreate,
    TrackerGoals,
    TrackerSummary,
    TrackerTotals,
)
from api.storage import DataStore

router = APIRouter(prefix="/api/tracker", tags=["tracker"])
store = DataStore()


@router.get("", response_model=TrackerSummary)
def get_tracker():
    goals = store.get_tracker_goals()
    entries = store.list_tracker_entries()
    totals = TrackerTotals(
        upvotes=sum(e.upvotes for e in entries),
        impressions=sum(e.impressions for e in entries),
    )
    return TrackerSummary(goals=goals, totals=totals, entries=entries)


@router.put("/goals", response_model=TrackerGoals)
def save_goals(goals: TrackerGoals):
    return store.save_tracker_goals(goals)


@router.post("/entries", response_model=TrackerEntry)
def add_entry(entry: TrackerEntryCreate):
    return store.add_tracker_entry(entry)