"""
MVP auth: a single shared secret plus a required X-Tenant-Id header.

This deliberately replaces Keycloak for the MVP. It is NOT production
identity - there's no per-user auth, no token expiry, no roles. It exists
so the rest of the codebase can depend on `get_current_tenant` and not
change shape when real auth (Keycloak/OIDC) is reintroduced.
"""
from fastapi import Header, HTTPException, status

from app.config import settings


def verify_shared_secret(authorization: str = Header(default="")) -> None:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_shared_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_tenant(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    _: None = None,
) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Tenant-Id header required")
    return x_tenant_id
