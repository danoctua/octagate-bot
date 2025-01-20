from typing import Iterable, overload

from sqlalchemy.exc import NoResultFound
from telegram import User as TelegramUser
from telethon.tl.types import User as TelethonUser

from core.dtos.user import TelegramUserDTO
from core.models.user import User
from core.services.base import BaseService


class UserService(BaseService):
    def get_by_telegram_id(self, telegram_id: int) -> User:
        return (
            self.db_session.query(User)
            .filter(
                User.telegram_id == telegram_id,
            )
            .one()
        )

    def get(self, user_id: int) -> User:
        return (
            self.db_session.query(User)
            .filter(
                User.id == user_id,
            )
            .one()
        )

    def get_all(self, telegram_ids: Iterable[int] | None = None) -> list[type[User]]:
        query = self.db_session.query(User)
        if telegram_ids:
            query = query.filter(User.telegram_id.in_(telegram_ids))

        return query.all()

    def get_all_prefetched(
        self,
        telegram_ids: Iterable[int] | None = None,
    ) -> list[User]:
        query = self.db_session.query(User)
        if telegram_ids:
            query = query.filter(User.telegram_id.in_(telegram_ids))

        return query.all()

    def create(self, telegram_user: TelegramUserDTO) -> User:
        new_user = User(
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            is_premium=telegram_user.is_premium,
            language=telegram_user.language_code,
        )
        self.db_session.add(new_user)
        self.db_session.commit()
        return new_user

    def update(self, user: User, telegram_user: TelegramUserDTO) -> User:
        user.language = telegram_user.language_code
        user.first_name = telegram_user.first_name
        user.last_name = telegram_user.last_name
        user.username = telegram_user.username
        user.is_premium = bool(telegram_user.is_premium)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    @overload
    def create_or_update(self, telegram_user: TelegramUser) -> User:
        ...

    @overload
    def create_or_update(self, telegram_user: TelethonUser) -> User:
        ...

    def create_or_update(self, telegram_user) -> User:
        if isinstance(telegram_user, TelethonUser):
            telegram_user_dto = TelegramUserDTO(
                id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                is_premium=telegram_user.premium,
                language_code=telegram_user.lang_code,
            )
        elif isinstance(telegram_user, TelegramUser):
            telegram_user_dto = TelegramUserDTO(
                id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                is_premium=telegram_user.is_premium,
                language_code=telegram_user.language_code,
            )
        else:
            raise ValueError(f"Unsupported user type: {type(telegram_user)}")

        try:
            user = self.get_by_telegram_id(telegram_user.id)
            return self.update(user=user, telegram_user=telegram_user_dto)
        except NoResultFound:
            return self.create(telegram_user_dto)

    def get_or_create(self, telegram_user: TelegramUserDTO) -> User:
        try:
            return self.get_by_telegram_id(telegram_user.id)
        except NoResultFound:
            return self.create(telegram_user)
