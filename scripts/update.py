import json
import os
import subprocess
import requests

from typing import List


def get_ips_from_masters(masters: List[str]) -> List[str]:
    cmd = f"./masterstat {' '.join(masters)} > servers.txt"
    subprocess.call(cmd, shell=True)

    with open("servers.txt", "r") as fp:
        server_addresses = fp.read().strip().splitlines()

    os.remove("servers.txt")

    server_ips = []

    for address in server_addresses:
        if ":" in address:
            server_ips.append(address.split(":", maxsplit=1)[0])

    return list(sorted(set(server_ips)))


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
                "region": entry["continent"],
                "country": entry["country"],
                "cc": entry["countryCode"],
                "city": entry["city"],
                "coordinates": [entry["lat"], entry["lon"]]
            }

    return ip_to_geo_map


if __name__ == '__main__':
    masters = [
        "master.quakeworld.nu:27000",
        "master.quakeservers.net:27000",
        "qwmaster.ocrana.de:27000",
        "qwmaster.fodquake.net:27000",
    ]

    ips = get_ips_from_masters(masters)
    min_expected_server_count = 150

    if len(ips) < min_expected_server_count:
        print("did not found that many ips, aborting.")
        exit(0)

    ip_to_geo_map = get_ip_to_geo_map(ips)

    with open("ip_to_geo.json", "w") as fp:
        json.dump(ip_to_geo_map, fp, indent=2)

    print(f"done. {len(ips)}")
