import jwt
import time
import os

def create_agent_token() -> str:
    private_key_path = os.environ.get("MCP_AUTH_PRIVATE_KEY_PATH", "/run/mcp-private/private_key.pem")
    
    with open(private_key_path, "r", encoding="utf-8") as f:
        private_key = f.read()

    payload = {
        "iss": "agente_a",
        "sub": "agente_a",
        "aud": "mcp-interoperability-server",  
        "exp": int(time.time()) + 3600,        
        "scope": "mcp:read mcp:tools"    
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")