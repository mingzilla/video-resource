from typing import Any, Dict

import httpx
from pydantic import BaseModel


class ProxyRequest:
    @staticmethod
    async def redirect(method: str, endpoint: str, model: BaseModel = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic proxy function for all HTTP methods."""
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            try:
                kwargs = {}
                if model:
                    kwargs["json"] = model.model_dump()
                if params:
                    kwargs["params"] = params

                response = await client.request(method, endpoint, **kwargs)
                response.raise_for_status()

                if method.upper() == "DELETE":
                    return {"message": "Resource deleted successfully"}
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise RuntimeError("Resource not found")
                raise RuntimeError(f"Request failed: {e}")
            except httpx.HTTPError as e:
                raise RuntimeError(f"Request failed: {e}")
