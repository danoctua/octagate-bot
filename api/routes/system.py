from fastapi import APIRouter, HTTPException

from api.pos.common import StatusFDO
from core.utils.task import wait_for_task

system_router = APIRouter(prefix="/system")


@system_router.get("/async-tasks/{task_id}")
async def get_task_status_status(
    task_id: str,
) -> StatusFDO:
    is_successful = await wait_for_task(task_id=task_id)
    if is_successful:
        return StatusFDO(status="success", message="Task is completed successfully")
    else:
        raise HTTPException(
            detail={"error": {"message": "Failed to complete the task"}},
            status_code=502,
        )
