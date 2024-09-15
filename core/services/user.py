from typing import Iterable

from sqlalchemy.exc import NoResultFound
from telegram import User as TelegramUser

from core.models.user import User
from core.services.base import BaseService


class UserService(BaseService):
    def get(self, telegram_id: int) -> User:
        return (
            self.db_session.query(User)
            .filter(
                User.telegram_id == telegram_id,
            )
            .one()
        )

    def get_all(self, telegram_ids: Iterable[int]) -> list[type[User]]:
        return (
            self.db_session.query(User)
            .filter(
                User.telegram_id.in_(telegram_ids),
            )
            .all()
        )

    def create(self, telegram_user: TelegramUser) -> User:
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

    def update(self, user: User, telegram_user: TelegramUser) -> User:
        user.language = telegram_user.language_code
        user.first_name = telegram_user.first_name
        user.last_name = telegram_user.last_name
        user.username = telegram_user.username
        user.is_premium = bool(telegram_user.is_premium)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def create_or_update(self, telegram_user: TelegramUser) -> User:
        try:
            user = self.get(telegram_user.id)
            return self.update(user=user, telegram_user=telegram_user)
        except NoResultFound:
            return self.create(telegram_user)

    def get_or_create(self, telegram_user: TelegramUser) -> User:
        try:
            return self.get(telegram_user.id)
        except NoResultFound:
            return self.create(telegram_user)
