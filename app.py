
import logging
import time
import httpx

from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mcp_integration.server_manager import mcp_server_manager

from pydantic import BaseModel, Field

from config import (
    APP_NAME,
    LLM_MODEL,
    LLM_PROVIDER,
    OPENROUTER_API_KEY,
    OPENROUTER_MODELS_URL,
    MODEL_CACHE_SECONDS
)

from llm_service import generate_response

from agent.agent_engine import agent_engine


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version="2.1.0",
    description="LLM Gateway with Model Switching, Agent and MCP Integration"
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# --------------------------------------------------
# HTML TEMPLATES
# --------------------------------------------------

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# MODEL CACHE
# --------------------------------------------------

model_cache = {
    "models": [],
    "last_updated": 0
}


# --------------------------------------------------
# REQUEST SCHEMAS
# --------------------------------------------------

class ChatMessage(BaseModel):

    role: Literal["user", "assistant"]

    content: str = Field(
        min_length=1,
        max_length=20000
    )


class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=20000
    )

    model: Optional[str] = None

    conversation: List[ChatMessage] = Field(
        default_factory=list,
        max_length=20
    )


# --------------------------------------------------
# OPENROUTER FREE MODEL RETRIEVAL
# --------------------------------------------------

def get_free_models(force_refresh=False):

    current_time = time.monotonic()

    cache_valid = (
        bool(model_cache["models"])
        and current_time - model_cache["last_updated"]
        < MODEL_CACHE_SECONDS
    )

    if cache_valid and not force_refresh:

        return model_cache["models"]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Accept": "application/json"
    }

    try:

        response = httpx.get(
            OPENROUTER_MODELS_URL,
            headers=headers,
            params={
                "output_modalities": "text"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json().get("data", [])

        free_models = []

        for model in data:

            model_id = model.get("id", "")

            architecture = model.get(
                "architecture", {}
            )

            output_modalities = architecture.get(
                "output_modalities", []
            )

            if (
                model_id.endswith(":free")
                and "text" in output_modalities
            ):

                free_models.append({

                    "id": model_id,

                    "name": model.get(
                        "name",
                        model_id
                    ),

                    "context_length": model.get(
                        "context_length"
                    ),

                    "description": model.get(
                        "description",
                        ""
                    )

                })

        free_models.sort(
            key=lambda item: item["name"].lower()
        )

        model_cache["models"] = free_models

        model_cache["last_updated"] = time.monotonic()

        logger.info(
            "Loaded %s OpenRouter free models",
            len(free_models)
        )

        return free_models

    except httpx.HTTPError:

        logger.exception(
            "Failed to retrieve OpenRouter models"
        )

        if model_cache["models"]:
            return model_cache["models"]

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve OpenRouter models."
        )


# --------------------------------------------------
# HELPER: VALIDATE MODEL
# --------------------------------------------------

def get_selected_model(requested_model=None):

    models = get_free_models()

    available_model_ids = {
        item["id"] for item in models
    }

    selected_model = requested_model or LLM_MODEL

    if (
        requested_model is None
        and selected_model not in available_model_ids
        and models
    ):

        selected_model = models[0]["id"]

    if selected_model not in available_model_ids:

        raise HTTPException(
            status_code=400,
            detail="Selected model is not an available OpenRouter free text model."
        )

    return selected_model


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={

            "app_name": APP_NAME,

            "provider": LLM_PROVIDER,

            "model": LLM_MODEL

        }

    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {

        "success": True,

        "status": "healthy",

        "provider": LLM_PROVIDER,

        "model": LLM_MODEL

    }


# --------------------------------------------------
# OPENROUTER FREE MODELS API
# --------------------------------------------------

@app.get("/api/models/free")
def list_free_models(refresh: bool = False):

    models = get_free_models(
        force_refresh=refresh
    )

    default_model = LLM_MODEL

    if models and not any(
        item["id"] == default_model
        for item in models
    ):

        default_model = models[0]["id"]

    return {

        "success": True,

        "provider": "openrouter",

        "total": len(models),

        "default_model": default_model,

        "models": models

    }


# --------------------------------------------------
# NORMAL CHAT API
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        logger.info(
            "New chat request received"
        )

        selected_model = get_selected_model(
            request.model
        )

        conversation = [

            item.model_dump()

            for item in request.conversation

        ] if request.conversation else None

        result = generate_response(

            user_message=request.message,

            conversation=conversation,

            model=selected_model

        )

        logger.info(
            "Chat response generated using %s",
            selected_model
        )

        return result

    except HTTPException:

        raise

    except Exception:

        logger.exception(
            "Chat request failed"
        )

        raise HTTPException(

            status_code=502,

            detail="Unable to generate AI response."

        )


# --------------------------------------------------
# AI AGENT API
# --------------------------------------------------

@app.post("/agent/run")
async def run_agent(request: ChatRequest):

    try:

        logger.info(
            "New agent request received: %s",
            request.message
        )

        selected_model = get_selected_model(
            request.model
        )

        conversation = [

            item.model_dump()

            for item in request.conversation

        ] if request.conversation else None

        result = await agent_engine.run(

            message=request.message,

            conversation=conversation,

            model=selected_model

        )

        logger.info(
            "Agent execution completed"
        )

        return result

    except HTTPException:

        raise

    except Exception:

        logger.exception(
            "Agent execution failed"
        )

        raise HTTPException(

            status_code=500,

            detail="Unable to execute agent request."

        )


# --------------------------------------------------
# STARTUP EVENT
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():

    logger.info("====================================")
    logger.info("Starting LLM Gateway")
    logger.info("Initializing MCP servers...")

    results = await mcp_server_manager.start_all()

    for server, result in results.items():

        logger.info(
            "MCP SERVER: %s | STATUS: %s",
            server,
            result
        )

    connected = await mcp_server_manager.list_servers()

    logger.info("CONNECTED MCP SERVERS: %s", connected)

    logger.info("LLM Gateway startup completed")
    logger.info("====================================")
# --------------------------------------------------
# SHUTDOWN EVENT
# --------------------------------------------------

@app.on_event("shutdown")
async def shutdown_event():

    logger.info("Shutting down LLM Gateway")

    try:

        from mcp_integration.server_manager import mcp_server_manager

        await mcp_server_manager.stop_all()

    except Exception:

        logger.exception(
            "MCP shutdown encountered an error"
        )
