from fastapi import APIRouter
from service.insert_twii_index import get_twii_daily_data

router = APIRouter()

@router.get("/daily")
def read_twii_daily():
    return get_twii_daily_data()
