import httpx
from app.core.config import settings


def trigger_recovery_campaign() -> dict:
    if not (
        settings.KIPPS_BEARER_TOKEN
        and settings.KIPPS_ORG_ID
        and settings.KIPPS_CAMPAIGN_ID
    ):
        return {
            "ok": False,
            "error": "Kipps campaign trigger not configured (missing env vars)",
        }

    url = f"{settings.KIPPS_BASE_URL}/campaign/campaigns/{settings.KIPPS_CAMPAIGN_ID}/resume/"
    headers = {
        "Authorization": f"Bearer {settings.KIPPS_BEARER_TOKEN}",
        "X-Organization-Id": settings.KIPPS_ORG_ID,
    }

    try:
        response = httpx.post(url, headers=headers, timeout=15)
        response.raise_for_status()
        return {"ok": True, "status_code": response.status_code}
    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "error": f"Kipps returned {e.response.status_code}: {e.response.text}",
        }
    except httpx.RequestError as e:
        return {"ok": False, "error": f"Request to Kipps failed: {e}"}
