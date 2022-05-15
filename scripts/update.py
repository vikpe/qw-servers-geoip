import json
import os
import subprocess

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


def get_country_info(ip: str) -> str:
    cmd = f"geoiplookup {ip} | awk -F': ' '{{print $2}}'"
    geoiplookup_response = subprocess.check_output(cmd, shell=True).decode().strip()

    error_needles = ["can't resolve hostname", "IP Address not found"]

    if any(n in geoiplookup_response for n in error_needles):
        return ""
    else:
        return geoiplookup_response


def get_cc_to_region_map() -> dict:
    with open("geo_data/cc_to_region.json", "r") as fp:
        return json.load(fp)


def get_ip_to_geo_map(ips: List[str]) -> dict:
    trans = {}
    cc_to_region_map = get_cc_to_region_map()

    for ip in sorted(ips):
        country_info = get_country_info(ip)

        if country_info:
            cc, country = country_info.split(", ", maxsplit=1)

            trans[ip] = {
                "cc": cc,
                "country": country,
                "region": cc_to_region_map.get(cc, "")
            }

    return trans


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
