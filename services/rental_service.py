from models.rental import RentalStatusEnum

def get_status_enum(r):
    if r.item_return_date:
        return RentalStatusEnum.RETURNED
    elif r.overdue > 0:
        return RentalStatusEnum.OVERDUE
    else:
        return RentalStatusEnum.BORROWED