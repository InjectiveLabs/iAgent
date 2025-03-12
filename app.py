import asyncio
from hypercorn.config import Config as HyperConfig
from hypercorn.asyncio import serve
from quart import Quart, request, jsonify
from quart_cors import cors
from src.chat_server.chat_service import InjectiveChatService
from src.injective_functions.utils.helpers import detailed_exception_info
app = Quart(__name__)
# Enable CORS for all routes
app = cors(app, allow_origin=["http://localhost:5173", "http://localhost:3000"])
chat_service = InjectiveChatService()

@app.route("/chat", methods=["POST"])
async def chat_endpoint():
    try:
        data = await request.get_json()
        print(data)
        if not data or "message" not in data:
            return jsonify({
                "type": "error",
                "content": "No message provided, Please provide a message to continue our conversation.",
                "session_id": data.get("session_id", "default"),
            }), 400
        
        response = await chat_service.get_response(
            message=data["message"],
            session_id=data.get("session_id", "default")
        )
        print("response: ", response)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "type": "error",
            "error": str(detailed_exception_info),
            "content": "I apologize, but I encountered an error. Please try again.",
            "session_id": data.get("session_id", "default") if data else "default",
        }), 500

@app.route("/history", methods=["GET"])
async def history_endpoint():
    session_id = request.args.get("session_id", "default")
    return jsonify({
        "history": chat_service.conversation_manager.get_history(session_id)
    })

@app.route("/clear", methods=["POST"])
async def clear_endpoint():
    session_id = request.args.get("session_id", "default")
    chat_service.conversation_manager.clear_history(session_id)
    return jsonify({"status": "success"})

@app.after_request
async def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    config = HyperConfig()
    config.bind = ["0.0.0.0:5000"]
    asyncio.run(serve(app, config))