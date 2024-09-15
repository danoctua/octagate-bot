from core.models.user import User


class NotPermittedException(Exception):
    ...


def has_general_permission(user: User) -> bool:
    return True
