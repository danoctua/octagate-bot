import logging

from pytonapi.schema.jettons import JettonInfo
from pytonapi.utils import to_amount
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
        return self.db_session.query(Jetton).filter(Jetton.is_enabled.is_(True)).all()
