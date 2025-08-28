from fastapi import APIRouter

router = APIRouter(tags=["admin"])

@router.get("/dashboard")
async def get_admin_dashboard():
    return {"status": "Admin access only"}