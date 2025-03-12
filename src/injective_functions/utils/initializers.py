from grpc import RpcError
from pyinjective.async_client import AsyncClient
from pyinjective.constant import GAS_FEE_BUFFER_AMOUNT, GAS_PRICE
from pyinjective.core.network import Network
from pyinjective.core.broadcaster import MsgBroadcasterWithPk
from pyinjective.transaction import Transaction
from pyinjective.wallet import PrivateKey
from src.injective_functions.utils.helpers import detailed_exception_info


class ChainInteractor:
    def __init__(self, network_type: str = "mainnet") -> None:
        # Remove private key dependency
        self.network_type = network_type
        self.network = Network.testnet() if network_type == "testnet" else Network.mainnet()
        self.client = None
        self.composer = None
        
        # Instead of creating from private key, we'll accept the address
        # from MetaMask later
        self.address = None

    async def init_client(self, address: str):
        """Initialize with a MetaMask address instead of private key"""
        #This is the metamask erc20 address?
        #We need to check if its ERC20 address or INJ native
        self.address = address  
        self.client = AsyncClient(self.network)
        self.composer = await self.client.composer()
        await self.client.sync_timeout_height()
        await self.client.fetch_account(self.address)

    async def prepare_unsigned_transaction(self, msg):
        """Prepare a transaction without signing it"""
        if not self.address:
            raise ValueError("Must initialize with address first")

        # Create transaction with the message
        tx = (
            Transaction()
            .with_messages(msg)
            .with_sequence(self.client.get_sequence())
            .with_account_num(self.client.get_number())
            .with_chain_id(self.network.chain_id)
        )

        # Calculate gas (we'll estimate this without simulation since we can't sign)
        gas_limit = GAS_FEE_BUFFER_AMOUNT * 2  # Conservative estimate
        gas_price = GAS_PRICE
        fee = [
            self.composer.coin(
                amount=gas_price * gas_limit,
                denom=self.network.fee_denom,
            )
        ]

        # Prepare final unsigned transaction
        tx = (
            tx.with_gas(gas_limit)
            .with_fee(fee)
            .with_memo("")
            .with_timeout_height(self.client.timeout_height)
        )

        # Return the unsigned transaction data
        return {
            "body": tx.body.SerializeToString().hex(),
            "auth_info": tx.auth_info.SerializeToString().hex(),
            "chain_id": self.network.chain_id,
            "account_number": str(self.client.get_number()),
            "sequence": str(self.client.get_sequence())
        }

    async def broadcast_signed_tx(self, signed_tx_data: str):
        """Broadcast a transaction that was signed by MetaMask"""
        return await self.client.broadcast_tx_sync_mode(signed_tx_data)