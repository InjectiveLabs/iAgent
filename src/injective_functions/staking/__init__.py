from src.injective_functions.base import InjectiveBase
from typing import Dict, List


"""This class handles all account transfer within the account"""


class InjectiveStaking(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def stake_tokens(self, validator_address: str, amount: str) -> Dict:
        # prepare tx msg
        msg = self.chain_client.composer.MsgDelegate(
            delegator_address=self.chain_client.address.to_acc_bech32(),
            validator_address=validator_address,
            amount=float(amount),
        )
        return await self.chain_client.build_and_broadcast_tx(msg)
