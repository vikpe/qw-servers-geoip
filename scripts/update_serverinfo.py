import json
import subprocess

from typing import List


def read_master_server(master_address: str) -> List[str]:
    hostname, port_bits = master_address.split(":")
    cmd = f"bash ./scripts/read_master_server.sh {hostname} {port_bits}"

    try:
        subprocess.call(cmd, shell=True)

    except subprocess.CalledProcessError:
        print(f"unable to read {master_address}")

    server_ips = []

    try:
        header_sequence = b"\xff\xff\xff\xffd\n"
        header_block_len = len(header_sequence)
        ip_block_len = 4
        port_block_len = 2
        server_bits = ip_block_len + port_block_len
        result_file = f"{hostname}.servers"

        with open(result_file, "rb") as fp:
            print(fp.read())
            fp.seek(0)
            _ = fp.read(header_block_len)

            while server_chunk := fp.read(server_bits):
                ip = ".".join(map(str, server_chunk[0:ip_block_len]))
                # port_bits = server_chunk[-port_block_len:]
                # port = (port_bits[0] << 8) + port_bits[1]
                server_ips.append(ip)
    except:
        pass

    return list(set(server_ips))


def gather_ips() -> List[str]:
    masters = [
        "master.quakeworld.nu:27000",
        "master.quakeservers.net:27000",
        "qwmaster.ocrana.de:27000",
        "qwmaster.fodquake.net:27000",
    ]

    all_server_ips = set()

    for master_address in masters:
        print(f"{master_address}: connect")
        server_ips = read_master_server(master_address)
        print(f"{master_address}: collected {len(server_ips)} ips")
        all_server_ips.update(server_ips)
        print()

    print(f"done, total {len(all_server_ips)} ips")

    return list(all_server_ips)


def get_country_info(ip: str) -> str:
    cmd = f"geoiplookup {ip} | awk -F': ' '{{print $2}}'"
    geoiplookup_response = subprocess.check_output(cmd, shell=True).decode().strip()

    error_needles = ["can't resolve hostname", "IP Address not found"]

    if any(n in geoiplookup_response for n in error_needles):
        return ""
    else:
        return geoiplookup_response


def get_alpha2_to_region_map() -> dict:
    with open("geo_data/alpha2_to_region.json", "r") as fp:
        return json.load(fp)


def get_ip_to_geo_map(ips: List[str]) -> dict:
    trans = {}
    alpha2_to_region_map = get_alpha2_to_region_map()

    for ip in ips:
        country_info = get_country_info(ip)

        if country_info:
            alpha2, country = country_info.split(", ", maxsplit=1)

            trans[ip] = {
                "alpha2": alpha2,
                "country": country,
                "region": alpha2_to_region_map.get(alpha2, "")
            }

    return trans


if __name__ == '__main__':
    ips = gather_ips()
    min_expected_server_count = 100

    if len(ips) < min_expected_server_count:
        print("did not found that many ips, aborting.")
        exit(0)

    ip_to_geo_map = get_ip_to_geo_map(ips)

    with open("ip_to_geo.json", "w") as fp:
        json.dump(ip_to_geo_map, fp, indent=2)
