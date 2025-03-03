import logging

from pytonapi.schema.jettons import JettonInfo
from pytonapi.utils import to_amount
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound

from core.models.blockchain import Jetton
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class JettonService(BaseService):
    def create(self, jetton_info: JettonInfo, logo_path: str) -> Jetton:
        jetton = Jetton(
            address=jetton_info.metadata.address.to_raw(),
            name=jetton_info.metadata.name,
            description=jetton_info.metadata.description,
            symbol=jetton_info.metadata.symbol,
            total_supply=to_amount(int(jetton_info.total_supply)),
            logo_path=logo_path,
        )
        self.db_session.add(jetton)
        self.db_session.commit()
        logger.info(f"Jetton {jetton.name!r} created.")
        return jetton

    def update(self, jetton_info: JettonInfo, jetton: Jetton, logo_path: str) -> Jetton:
        jetton.name = jetton_info.metadata.name
        jetton.description = jetton_info.metadata.description
        jetton.symbol = jetton_info.metadata.symbol
        jetton.total_supply = to_amount(int(jetton_info.total_supply))
        jetton.logo_path = logo_path
        self.db_session.commit()
        logger.info(f"Jetton {jetton.name!r} updated.")
        return jetton

    def update_status(self, address: str, is_enabled: bool) -> Jetton:
        jetton = self.get(address=address)
        jetton.is_enabled = is_enabled
        self.db_session.commit()
        logger.info(f"Jetton {jetton.name!r} status updated.")
        return jetton

    def create_or_update(self, jetton_info: JettonInfo, logo_path: str) -> Jetton:
        try:
            jetton = self.get(address=jetton_info.metadata.address.to_raw())
            return self.update(jetton_info, jetton, logo_path=logo_path)
        except NoResultFound:
            logger.info(
                f"No jetton for address {jetton_info.metadata.address!r} found. Creating new jetton."
            )
            return self.create(jetton_info, logo_path=logo_path)

    def get(self, address: str) -> Jetton:
        return self.db_session.query(Jetton).filter(Jetton.address == address).one()

    def get_whitelisted(self) -> list[Jetton]:
        return (
            self.db_session.query(Jetton)
            .filter(Jetton.is_enabled.is_(True))
            .order_by(Jetton.created_at)
            .all()
        )

    def get_all(self, whitelisted_only: bool) -> list[Jetton]:
        query = self.db_session.query(Jetton)
        if whitelisted_only:
            query = query.filter(Jetton.is_enabled.is_(True))
            query = query.order_by(Jetton.created_at)
        else:
            query = query.order_by(desc(Jetton.is_enabled), Jetton.created_at)

        return query.all()
