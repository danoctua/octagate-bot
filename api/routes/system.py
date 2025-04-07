import random

from fastapi import APIRouter, HTTPException

from api.pos.common import StatusFDO
from core.dtos.chat.rules.whitelist import WhitelistRuleCPO
from core.utils.task import wait_for_task

system_router = APIRouter(prefix="/system", tags=["System"])
system_non_authenticated_router = APIRouter(prefix="/system", tags=["System", "Test"])


@system_router.get("/async-tasks/{task_id}")
async def get_task_status_status(
    task_id: str,
) -> StatusFDO:
    is_successful = await wait_for_task(task_id=task_id)
    if is_successful:
        return StatusFDO(status="success", message="Task is completed successfully")
    else:
        raise HTTPException(
            detail="Failed to complete the task",
            status_code=502,
        )


@system_non_authenticated_router.get("/test-get-random-users-list")
async def get_random_users_list() -> WhitelistRuleCPO:
    return WhitelistRuleCPO(
        users=[random.randint(1234567, 23456789) for _ in range(10)]
    )
