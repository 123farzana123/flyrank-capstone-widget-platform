import httpx


def get_geo_from_ip(ip_address: str) -> dict:
    """
    Look up country/city for an IP, trying provider A then provider B.
    Returns {"country": ..., "city": ...} with None values if both fail —
    enrichment must never block a submission from being saved.
    """
    # Provider A: ip-api.com
    try:
        resp = httpx.get(f"http://ip-api.com/json/{ip_address}", timeout=3)
        data = resp.json()
        if data.get("status") == "success":
            return {"country": data.get("country"), "city": data.get("city")}
    except Exception:
        pass  # provider A failed, try provider B

    # Provider B: ipapi.co
    try:
        resp = httpx.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
        data = resp.json()
        if not data.get("error"):
            return {"country": data.get("country_name"), "city": data.get("city")}
    except Exception:
        pass  # provider B also failed

    # Both failed — degrade gracefully, no geo data
    return {"country": None, "city": None}