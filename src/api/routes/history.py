from typing import List

from fastapi import APIRouter

from api.schemas import HistoryCreate, HistoryEntry
from api.storage import DataStore

router = APIRouter(prefix="/api/history", tags=["history"])
store = DataStore()


@router.get("", response_model=List[HistoryEntry])
def list_history():
    return store.list_history()


@router.post("", response_model=HistoryEntry)
def add_history(entry: HistoryCreate):
    return store.add_history(entry)