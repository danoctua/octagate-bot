import logging

from pytonapi.schema.jettons import JettonHolders

from core.models.wallet import UserWallet, JettonWallet
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class UserWalletExistError(Exception):
    pass


class WalletService(BaseService):
    def connect_user_wallet(self, user_id: int, wallet_address: str) -> None:
        existing_user_wallet = self.get_user_wallet(wallet_address)
        if existing_user_wallet:
            logger.warning(f"User %s is trying to connect already connected wallet %s", user_id, wallet_address)
            raise UserWalletExistError(f"User {user_id} is trying to connect already connected wallet {wallet_address}")

        new_wallet = UserWallet(user_id=user_id, address=wallet_address)
        self.db_session.add(new_wallet)
        self.db_session.commit()

    def get_user_wallet(self, wallet_address: str) -> UserWallet | None:
        return self.db_session.query(UserWallet).filter(
            UserWallet.address == wallet_address
        ).first()

    def disconnect_user_wallet(self, user_id: int) -> None:
        wallet = self.db_session.query(UserWallet).filter(
            UserWallet.user_id == user_id,
        ).delete()
        self.db_session.commit()

    def link_user_jetton_wallet(self, wallet_address: str) -> None:
        user_wallet = self.db_session.query(UserWallet).filter(
            UserWallet.address == wallet_address
        ).first()
        jetton_wallet = self.db_session.query(JettonWallet).filter(
            JettonWallet.address == wallet_address
        ).first()
        if user_wallet and jetton_wallet:
            if user_wallet.jetton_wallet_address != wallet_address:
                user_wallet.jetton_wallet_address = wallet_address
                self.db_session.add(user_wallet)
                self.db_session.flush()
                logger.info(f"Linked user wallet {wallet_address} to jetton wallet")
                return

            logger.debug(f"User wallet {wallet_address} is already linked to jetton wallet")
            return

        logger.debug(f"User wallet {wallet_address} or jetton wallet {wallet_address} not found")

    def _add_jetton_wallet(self, wallet_address: str, balance: int, rating: int) -> None:
        new_wallet = JettonWallet(address=wallet_address, balance=balance, rating=rating)
        self.db_session.add(new_wallet)
        logger.debug(f"Added jetton wallet {wallet_address}")

    def _update_jetton_wallet(self, wallet_address: str, balance: int, rating: int) -> None:
        wallet = self.db_session.query(JettonWallet).filter(
            JettonWallet.address == wallet_address
        ).one()
        if wallet.balance == balance and wallet.rating == rating:
            logger.debug(f"Jetton wallet {wallet_address} has not changed")
            return
        wallet.balance = balance
        wallet.rating = rating
        self.db_session.add(wallet)
        logger.debug(f"Updated jetton wallet {wallet_address}")

    def jetton_wallet_exists(self, wallet_address: str) -> bool:
        return self.db_session.query(JettonWallet).filter(
            JettonWallet.address == wallet_address
        ).count() > 0

    def get_jetton_wallet(self, wallet_address: str) -> JettonWallet:
        return self.db_session.query(JettonWallet).filter(
            JettonWallet.address == wallet_address
        ).one()

    def add_or_update_jetton_wallet(self, wallet_address: str, balance: int, rating: int) -> None:
        if self.jetton_wallet_exists(wallet_address):
            self._update_jetton_wallet(wallet_address, balance, rating)
        else:
            self._add_jetton_wallet(wallet_address, balance, rating)

        self.db_session.flush()

    def bulk_update_jetton_holders(self, wallets: JettonHolders) -> None:
        for rating, wallet in enumerate(wallets.addresses, start=1):
            self.add_or_update_jetton_wallet(wallet.owner.address.to_raw(), int(wallet.balance), rating)
            self.link_user_jetton_wallet(wallet.owner.address.to_raw())
            self.db_session.commit()
