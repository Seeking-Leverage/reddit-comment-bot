from typing import List

from fastapi import APIRouter

from api.schemas import PlaybookEntry
from api.storage import DataStore

router = APIRouter(prefix="/api/playbooks", tags=["playbooks"])
store = DataStore()


@router.get("", response_model=List[PlaybookEntry])
def list_playbooks():
    return store.list_playbooks()


@router.put("", response_model=List[PlaybookEntry])
def save_playbooks(playbooks: List[PlaybookEntry]):
    return store.save_playbooks(playbooks)