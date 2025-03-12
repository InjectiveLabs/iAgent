from decimal import Decimal
from src.injective_functions.base import InjectiveBase
from typing import Dict, List
from src.injective_functions.utils.indexer_requests import fetch_decimal_denoms
from src.injective_functions.utils.helpers import detailed_exception_info


class InjectiveBank(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def transfer_funds(
        self, amount: Decimal, denom: str = None, to_address: str = None
    ) -> Dict:

        msg = self.chain_client.composer.MsgSend(
            from_address=self.chain_client.address.to_acc_bech32(),
            to_address=str(to_address),
            amount=float(amount),
            denom=denom,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def query_balances(self, denom_list: List[str] = None) -> Dict:
        try:

            denoms: Dict[str, int] = await fetch_decimal_denoms(
                self.chain_client.network_type
            )
            bank_balances = await self.chain_client.client.fetch_bank_balances(
                address=self.chain_client.address.to_acc_bech32()
            )
            bank_balances = bank_balances["balances"]

            # hash the bank balances as a kv pair
            human_readable_balances = {}
            for token in bank_balances:
                if token["denom"] in denoms:
                    human_readable_balances[token["denom"]] = str(
                        int(token["amount"]) / 10 ** int(denoms[token["denom"]])
                    )
            # check if denom is an arg fron the openai func calling
            filtered_balances = dict()
            if denom_list != None:
                # filter the balances
                # TODO: replace with lambda func
                for denom in denom_list:
                    if denom in human_readable_balances:
                        filtered_balances[denom] = human_readable_balances[denom]
                    else:
                        filtered_balances[denom] = "The token is not on mainnet!"
                return {"success": True, "result": filtered_balances}

            else:
                return {"success": True, "result": human_readable_balances}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def query_spendable_balances(self, denom_list: List[str] = None) -> Dict:
        try:
            denoms: Dict[str, int] = await fetch_decimal_denoms(
                self.chain_client.network_type
            )
            bank_balances = await self.chain_client.client.fetch_spendable_balances(
                address=self.chain_client.address.to_acc_bech32()
            )
            bank_balances = bank_balances["balances"]
            # hash the bank balances as a kv pair
            human_readable_balances = {
                token["denom"]: str(
                    int(token["amount"]) / 10 ** int(denoms[token["denom"]])
                )
                for token in bank_balances
                if token["denom"] in denoms
            }

            # check if denom is an arg fron the openai func calling
            filtered_balances = dict()
            if denom_list != None:
                # filter the balances
                # TODO: replace with lambda func
                for denom in denom_list:
                    if denom in human_readable_balances:
                        filtered_balances[denom] = human_readable_balances[denom]
                    else:
                        filtered_balances[denom] = "The token is not on mainnet!"
                return {"success": True, "result": filtered_balances}

            else:
                return {"success": True, "result": human_readable_balances}

        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def query_total_supply(self, denom_list: List[str] = None) -> Dict:
        try:
            # we request this over and over again because new tokens can be added
            denoms: Dict[str, int] = await fetch_decimal_denoms(
                self.chain_client.network
            )
            total_supply = await self.chain_client.client.fetch_total_supply()
            total_supply = total_supply["supply"]
            human_readable_supply = {
                token["denom"]: str(
                    int(token["amount"]) / 10 ** int(denoms[token["denom"]])
                )
                for token in total_supply
                if token["denom"] in denoms
            }

            # check if denom is an arg fron the openai func calling
            filtered_supply = dict()
            if denom_list != 0:
                # filter the balances
                # TODO: replace with lambda func
                for denom in denom_list:
                    if denom in human_readable_supply:
                        filtered_supply[denom] = human_readable_supply[denom]
                    else:
                        filtered_supply[denom] = "The token is not on mainnet!"
                return {"success": True, "result": filtered_supply}

            else:
                return {"success": True, "result": human_readable_supply}

        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
