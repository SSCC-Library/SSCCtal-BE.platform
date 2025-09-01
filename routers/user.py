from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from models.rental import Rental
from models.item import Item
from models.item_copy import ItemCopy
from database import get_db
from new_schemas.response import CommonResponse
from new_schemas.rental import RentalMainInfo,RentalMainInfoWithItem
from security import get_current_user


router = APIRouter(prefix="/users", tags=["users"])

size = 12

@router.get("/items/rental-records",response_model=CommonResponse[list[RentalMainInfoWithItem]])
async def get_my_rentals(page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    student_id: int =Depends(get_current_user),db: Session = Depends(get_db)) :
    query = (
        db.query(Rental)
        .join(ItemCopy, Rental.copy_id == ItemCopy.copy_id)
        .join(Item, ItemCopy.item_id == Item.item_id)
        .filter(Rental.student_id == student_id)
    )
    count=query.count()
    offset = (page - 1) * size
    rentals = query.offset(offset).limit(size).all()

    if not rentals:
        return CommonResponse(
        success= False,
        code= 404
        )
    
    result = []
    for rental in rentals:
        rental_info = RentalMainInfo.model_validate(rental, from_attributes=True)
        result.append(RentalMainInfoWithItem(rental=rental_info,
                                             item_name=rental.item_copy.item.name))

    return CommonResponse(
        success= True,
        code= 200,
        data= result,
        total=count,
        page= page,
        size= size
    )
