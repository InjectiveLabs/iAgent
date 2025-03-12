from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
            )

        self.schema_paths = [
            "./src/injective_functions/account/account_schema.json",
            "./src/injective_functions/auction/auction_schema.json",
            "./src/injective_functions/authz/authz_schema.json",
            "./src/injective_functions/bank/bank_schema.json",
            "./src/injective_functions/exchange/exchange_schema.json",
            "./src/injective_functions/staking/staking_schema.json",
            "./src/injective_functions/token_factory/token_factory_schema.json",
            "./src/injective_functions/wasm/wasm_schema.json",
            "./src/injective_functions/utils/mito_get_requests_schema.json",
        ]
