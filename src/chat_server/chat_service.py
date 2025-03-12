from openai import OpenAI
import json
import asyncio
from src.chat_server.config import Config
from src.chat_server.conversation_manager import ConversationManager
from src.injective_functions.utils.function_helper import FunctionSchemaLoader
from src.injective_functions.utils.helpers import detailed_exception_info
PROMPT_CONTENT =  """You are a helpful AI assistant on Injective Chain. 
                    You will be answering all things related to injective chain, and help out with
                    on-chain functions.
                    
                    When handling market IDs, always use these standardized formats:
                    - For BTC perpetual: "BTC/USDT PERP" maps to "btcusdt-perp"
                    - For ETH perpetual: "ETH/USDT PERP" maps to "ethusdt-perp"
                    
                    When users mention markets:
                    1. If they use casual terms like "Bitcoin perpetual" or "BTC perp", interpret it as "BTC/USDT PERP"
                    2. If they mention "Ethereum futures" or "ETH perpetual", interpret it as "ETH/USDT PERP"
                    3. Always use the standardized format in your responses
                    
                    Before performing any action:
                    1. Describe what you're about to do
                    2. Ask for explicit confirmation
                    3. Only proceed after receiving a "yes"
                    
                    When making function calls:
                    1. Convert the standardized format (e.g., "BTC/USDT PERP") to the internal format (e.g., "btcusdt-perp")
                    2. When displaying results to users, convert back to the standard format
                    3. Always confirm before executing any functions
                    
                    For general questions, provide informative responses.
                    When users want to perform actions, describe the action and ask for confirmation but for fetching data you dont have to ask for confirmation.""",


# Let us render all the data requests here
# Function call on the transactions are something that I need to think about
class InjectiveChatService:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.conversation_manager = ConversationManager()
        self.function_schemas = FunctionSchemaLoader.load_schemas(
            self.config.schema_paths
        )

    async def get_response(self, message: str, session_id: str = "default"):
        try:
            # Add user message to conversation
            self.conversation_manager.add_message(
                session_id, {"role": "user", "content": message}
            )

            # Get initial response from OpenAI
            response = await self._get_openai_response(session_id)
            response_message = response.choices[0].message

            # Handle function calling if present
            if (
                hasattr(response_message, "function_call")
                and response_message.function_call
            ):
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)

                # Add function call to conversation
                self.conversation_manager.add_message(
                    session_id,
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    },
                )
                
                # Return the function call details
                return {
                    "type": "function_call",
                    "content": {"function_name": function_name, "arguments": function_args},
                    "session_id": session_id,
                }

            # Handle regular response
            content = response_message.content or self._get_default_response()
            self.conversation_manager.add_message(
                session_id, {"role": "assistant", "content": content}
            )

            return {"type": "message", "content": content, "session_id": session_id}

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(detailed_exception_info(e))}"
            return {
                "type": "error",
                "content": error_msg,
                "session_id": session_id,
            }

    async def _get_openai_response(self, session_id: str):
        return await asyncio.to_thread(
            self.client.chat.completions.create,
            model="gpt-4o",
            messages=self._get_messages_with_system_prompt(session_id),
            functions=self.function_schemas,
            function_call="auto",
            max_tokens=2000,
            temperature=0.7,
        )

    def _get_messages_with_system_prompt(self, session_id: str):
        system_message = {
            "role": "system",
            "content": str(PROMPT_CONTENT)
        }
        return [system_message] + self.conversation_manager.get_history(session_id)

    def _get_default_response(self):
        return "I'm here to help you with trading on Injective Chain. How can I assist you today?"
