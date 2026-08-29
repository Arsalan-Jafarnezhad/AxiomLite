"""Client IP address and (optional, offline) IP-to-country lookup helpers.

The country lookup expects an ``ip-country.csv`` file (three columns:
range start, range end, ISO country code) next to this module. It's not
shipped in this repo (size), so the loader degrades gracefully to "unknown
country" instead of crashing when the file is absent.
"""

from bisect import bisect_right
from functools import lru_cache
from ipaddress import ip_address
from pathlib import Path

from django.http import HttpRequest

_IP_COUNTRY_CSV = Path(__file__).with_name("ip-country.csv")


def get_user_ip_address(request: HttpRequest) -> str | None:
    """Best-effort client IP, honouring a reverse proxy's X-Forwarded-For."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@lru_cache(maxsize=1)
def _load_ip_country_db() -> tuple[list[int], list[tuple[int, str]]]:
    starts: list[int] = []
    ranges: list[tuple[int, str]] = []

    if not _IP_COUNTRY_CSV.exists():
        return starts, ranges

    with _IP_COUNTRY_CSV.open("r", encoding="utf-8") as f:
        for line in f:
            start, end, country = line.rstrip().split(",")
            starts.append(int(ip_address(start)))
            ranges.append((int(ip_address(end)), country))

    return starts, ranges


def get_country_by_ip(ip: str | None) -> str | None:
    """Returns the ISO country code for *ip*, or ``None`` if unknown/unavailable."""
    if not ip:
        return None

    # try:
    #     ip_int = int(ip_address(ip))
    # except ValueError:
    #     return None

    # starts, ranges = _load_ip_country_db()
    # if not starts:
    #     return None

    # i = bisect_right(starts, ip_int) - 1
    # if i >= 0:
    #     end, country = ranges[i]
    #     if ip_int <= end:
    #         return country

    return None
if __name__ == "__main__":
    ip_list = [
         "136.16.1.3",
 "136.19.1.201",
 "136.22.1.2 ",
    ]
    for ip in ip_list:
        print(f"{ip}: {get_country_by_ip(ip)}")