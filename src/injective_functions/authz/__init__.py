from src.injective_functions.utils.helpers import detailed_exception_info
from src.injective_functions.base import InjectiveBase
from typing import Dict, List


"""This class handles all auction messages"""


# TODO: add fetch current round function on indexer helper
class InjectiveAuthz(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    # TODO: make sure the messages are handled properly
    async def grant_address_auth(
        self, grantee_address: str, msg_type: str, duration: int
    ) -> Dict:

        msg = self.chain_client.composer.MsgGrantGeneric(
            granter=self.chain_client.address.to_acc_bech32(),
            grantee=grantee_address,
            msg_type=msg_type,
            expire_in=duration,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    # TODO: make sure the messages are handled properly
    async def revoke_address_auth(self, grantee_address: str, msg_type: str) -> Dict:

        msg = self.chain_client.composer.MsgRevoke(
            granter=self.chain_client.address.to_acc_bech32(),
            grantee=grantee_address,
            msg_type=msg_type,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def fetch_grants(self, granter: str, grantee: str, msg_type: str) -> Dict:
        try:
            res = await self.chain_client.client.fetch_grants(
                granter=granter, grantee=grantee, msg_type_url=msg_type
            )

            return {
                "success": True,
                "result": res,
            }
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
