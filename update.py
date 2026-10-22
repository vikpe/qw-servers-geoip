import json
from typing import List

import pycountry
import requests


def get_quakeworld_server_ips() -> List[str]:
    res = requests.get("https://api.quake.world/v1/servers")
    res.raise_for_status()
    return [server["ip"] for server in res.json()]


def get_qwleague_servers() -> List[dict]:
    res = requests.get("https://qwleague.com/api/servers")
    res.raise_for_status()
    return res.json()["items"]


def get_server_ips(qwleague_servers: List[dict]) -> List[str]:
    qwleague_ips = [server["ip"] for server in qwleague_servers]
    return sorted(set(get_quakeworld_server_ips() + qwleague_ips))


def chunks(arr: list, size: int):
    for i in range(0, len(arr), size):
        yield arr[i:i + size]


def get_ip_to_geo_map(ips: List[str]) -> dict:
    geo_api_url = "http://ip-api.com/batch?fields=status,message,continent,country,countryCode,city,lat,lon,query"

    ip_to_geo_map = {}

    for ip_chunk in list(chunks(ips, 100)):
        geodata = requests.post(geo_api_url, json=ip_chunk).json()

        for entry in geodata:
            ip_to_geo_map[entry["query"]] = {
                "region": entry.get("continent", "unknown"),
                "country": entry.get("country", "unknown"),
                "cc": entry.get("countryCode", "unknown"),
                "city": entry.get("city", "unknown"),
                "coordinates": [entry.get("lat", 0), entry.get("lon", 0)]
            }

    return ip_to_geo_map


CONTINENT_NAMES = {
    "af": "Africa",
    "as": "Asia",
    "eu": "Europe",
    "na": "North America",
    "oce": "Oceania",
    "sa": "South America",
}


def apply_qwleague_overrides(ip_to_geo_map: dict, qwleague_servers: List[dict]):
    # qwleague is authoritative for its own servers, geoip lookup is often off
    for server in qwleague_servers:
        geo = ip_to_geo_map.get(server["ip"])

        if geo is None:
            continue

        if server.get("continent"):
            geo["region"] = CONTINENT_NAMES.get(server["continent"], geo["region"])

        cc = (server.get("country") or "").upper()

        if cc and cc != geo["cc"]:
            country = pycountry.countries.get(alpha_2=cc)
            geo["cc"] = cc
            geo["country"] = country.name if country else cc

        if server.get("city"):
            geo["city"] = server["city"]


if __name__ == '__main__':
    qwleague_servers = get_qwleague_servers()
    ips = get_server_ips(qwleague_servers)
    min_expected_server_count = 150

    if len(ips) < min_expected_server_count:
        print("did not found that many ips, aborting.")
        exit(0)

    ip_to_geo_map = get_ip_to_geo_map(ips)
    apply_qwleague_overrides(ip_to_geo_map, qwleague_servers)

    with open("ip_to_geo.json", "w") as fp:
        json.dump(ip_to_geo_map, fp, indent=2)

    print(f"done. {len(ips)}")
