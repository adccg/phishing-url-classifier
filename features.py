from urllib.parse import urlparse


def extract_features(url: str) -> dict:
    """Turn a link into numbers, using only the protocol and the domain name."""
    url = url.strip()
    if "://" not in url:
        url = "http://" + url
    try:
        parsed = urlparse(url)
        domain = (parsed.hostname or "").lower()
        scheme = parsed.scheme.lower()
    except ValueError:
        domain, scheme = "", ""

    parts = domain.split(".") if domain else []
    tld = parts[-1] if parts else ""
    digits = sum(ch.isdigit() for ch in domain)

    return {
        "is_https": int(scheme == "https"),
        "domain_length": len(domain),
        "num_dots": domain.count("."),
        "num_hyphens": domain.count("-"),
        "num_digits": digits,
        "digit_ratio": digits / len(domain) if domain else 0.0,
        "is_ip_address": int(domain.replace(".", "").isdigit()),
        "tld_length": len(tld),
        "num_subdomains": max(len(parts) - 2, 0),
    }