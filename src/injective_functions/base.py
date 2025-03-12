from typing import Optional
from src.injective_functions.utils.initializers import ChainInteractor


class InjectiveBase:
    """Base class for all Injective modules providing shared functionality."""

    def __init__(self, chain_client: ChainInteractor):
        """
        Initialize base class with a chain client.

        Args:
            chain_client (ChainInteractor): Initialized chain client for interacting with the Injective blockchain
        """
        self.chain_client = chain_client

    @classmethod
    def with_params(
        cls, private_key: str, network_type: str = "mainnet"
    ) -> "InjectiveBase":
        """
        Alternative constructor that creates a new ChainInteractor instance.

        Args:
            private_key (str): Private key for blockchain interactions
            network_type (str, optional): Network type ("mainnet" or "testnet"). Defaults to "mainnet".

        Returns:
            InjectiveBase: Instance with new ChainInteractor
        """
        chain_client = ChainInteractor(
            network_type=network_type, private_key=private_key
        )
        return cls(chain_client)
