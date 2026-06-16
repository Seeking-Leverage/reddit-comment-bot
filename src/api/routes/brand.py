from fastapi import APIRouter

from api.schemas import BrandProfile
from api.storage import DataStore

router = APIRouter(prefix="/api/brand", tags=["brand"])
store = DataStore()


@router.get("", response_model=BrandProfile)
def get_brand():
    return store.get_brand()


@router.put("", response_model=BrandProfile)
def save_brand(brand: BrandProfile):
    return store.save_brand(brand)