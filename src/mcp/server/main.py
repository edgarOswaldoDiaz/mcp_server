from fastapi import FastAPI, HTTPException, Request
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from src.mcp.auth.oauth_handler import verify_access_token
from src.mcp.auth.oauth_router import router as oauth_router
from src.mcp.server.auth import create_auth
from src.mcp.server.metadata import SERVER_DESCRIPTION, SERVER_NAME
from src.mcp.server.prompts import register_prompts
from src.mcp.server.resources import register_resources
from src.mcp.server.tools import register_tools

MCP_PATH = "/mcp"


def create_server(use_auth: bool = True) -> FastMCP:
    auth = create_auth() if use_auth else None

    mcp = FastMCP(
        name=SERVER_NAME,
        instructions=SERVER_DESCRIPTION,
        auth=auth,
    )

    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)

    return mcp


class DPoPGuard:
    """Middleware ASGI: nada bajo /mcp pasa sin 'Authorization: DPoP' + prueba valida.

    Es ASGI puro (no BaseHTTPMiddleware) para no romper el streaming de MCP.
    """

    def __init__(self, app, protected_prefix: str = MCP_PATH):
        self.app = app
        self.prefix = protected_prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix):
            try:
                verify_access_token(Request(scope))
            except HTTPException as e:
                response = JSONResponse({"detail": e.detail}, status_code=e.status_code,
                                        headers=e.headers)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


def create_app() -> FastAPI:
    # El MCP se sirve como app ASGI; la autenticacion la hace OAuth+DPoP (DPoPGuard),
    # por eso el MCP interno va con use_auth=False (ya no usa los .pem).
    mcp = create_server(use_auth=False)
    mcp_app = mcp.http_app(path=MCP_PATH)

    # Sin /docs, /redoc ni /openapi.json: son rutas publicas y no deben describir la API a nadie.
    app = FastAPI(title="MCP Server con OAuth 2.0 + DPoP", lifespan=mcp_app.lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(oauth_router)
    app.mount("/", mcp_app)
    app.add_middleware(DPoPGuard)
    return app


mcp_instance = create_server(use_auth=False)   # compatibilidad con tests existentes
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
