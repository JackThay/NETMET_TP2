"""execute each exercise or correction for TP1"""
import requests
import random
import sys

from pathlib import Path

from common.credentials import get_ripe_atlas_credentials
from common.file_utils import dump_json, load_json, insert_json
from common.default import (
    TP2_VPS_DATASET,
    TP2_TARGETS_DATASET,
    TP2_VPS_DATASET_CORRECTION,
    TP2_TARGETS_DATASET_CORRECTION,
    TP2_RESULTS_PATH,
)
from common.ripe.utils import print_traceroute
from common.logger_config import logger


def get_one_vp_one_target_random() -> tuple:
    """return one vp from set of vp and one target from set of target"""

    # first we will load targets and vps from last exercise
    try:
        targets = load_json(TP2_TARGETS_DATASET)  # all UA connected servers
        vps = load_json(TP2_VPS_DATASET)  # all RU connected servers
    except FileNotFoundError:
        logger.info(f"using vps and targets from the correction")

        targets = load_json(TP2_TARGETS_DATASET_CORRECTION)  # all UA connected servers
        vps = load_json(TP2_VPS_DATASET_CORRECTION)  # all RU connected servers

    # we get one random target and one random vp,
    # so we do not overload one specific pair with our measurements
    target_index = random.randint(0, len(targets) - 1)
    target = targets[target_index]

    vp_index = random.randint(0, len(vps) - 1)
    vp = vps[vp_index]

    logger.info(f"You got: vp = {vp} and target = {target}")

    return vp, target


def exo1_get_a_measurement(measurement_id: int, output_file_path: Path) -> dict:
    """
    retrieve a measurement using RIPE Atlas API, using a measurement uuid

    hints: requests package import
    """
    logger.info("###############################################")
    logger.info("#  EXO1                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/measurements/"

    ####################################################################
    # TODO: make an http request to RIPE API (using requests package)  #
    # to get measurement with measurement id : 38333397                #
    ####################################################################
    measurement_description: dict = requests.get(f"{base_url}/{measurement_id}/").json()

    if not measurement_description:
        logger.error("Measurement description is empty")
        sys.exit(1)

    logger.info("Measurement description")
    for key, val in measurement_description.items():
        logger.info(f"{key} : {val}")

    dump_json(measurement_description, output_file_path)

    return measurement_description


def exo2_get_a_measurement_result(measurement_id: int, output_file_path: Path) -> list:
    """
    retrieve a measurement using RIPE Atlas API, using a measurement uuid

    hints:
        - use requests python package for getting measurement description
        - check within measurement description to get measurement results url
    """
    logger.info("###############################################")
    logger.info("#  EXO2                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/measurements/"

    ####################################################################
    # TODO: make an http request to RIPE API (using requests package)  #
    # to get measurement results for measurement uuid 38333397         #
    ####################################################################

    # 1. get measurement description
    response = requests.get(f"{base_url}/{measurement_id}/").json()

    if not response:
        logger.error("measurement description is empty")
        sys.exit(1)

    # 2. check measurement description to get measurement results url
    result_url = response["result"]

    if not result_url:
        logger.error("result url empty")
        sys.exit(1)

    # 3. make the request to get measurement results
    results = requests.get(result_url).json()

    if not result_url:
        logger.error("Measurement results empty")
        sys.exit(1)

    # 4. just take the first result
    results = results[0]

    logger.info("Results:")
    for key, val in results.items():
        logger.info(f"{key} : {val}")
    logger.info("\n")

    # 5. from measurement result, get:
    #   - the source address of the measurement
    #   - the destination address of the measurement
    #   - the type of the measurement
    src_addr = results["src_addr"]
    dst_addr = results["dst_addr"]
    measurement_type = results["type"]

    logger.info(f"measurement source : {src_addr}")
    logger.info(f"measurement dst : {dst_addr}")
    logger.info(f"measurement type   : {measurement_type} \n")

    # 6. get actual measurement results
    traceroute = results["result"]

    # 7. print the traceroute
    logger.info("Traceroute results")
    if traceroute:
        print_traceroute(traceroute)

        dump_json(results, output_file_path)

        return traceroute


def exo3_get_all_vps() -> None:
    """get all connected servers from UA
    hints: we can add parameters to requests using the keyword params
    hints : params is a python dictionary
    """
    logger.info("###############################################")
    logger.info("#  EXO3                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/probes/"

    # 1. set parameters
    params = {"country_code": "UA"}

    if not params:
        logger.error("you must set parameters")
        sys.exit(1)
    else:
        # 2. perform request to get all RIPE Atlas servers in Ukraine
        response = requests.get(url=base_url, params=params).json()

        # 3. filter servers so they all :
        #   - have connected status (check the response)
        #   - have an IPv4 address
        filtered_vps = []
        for vp in response["results"]:
            if vp["status"]["name"] == "Connected":
                if vp["address_v4"]:
                    filtered_vps.append(vp)

        if filtered_vps:
            logger.info(f"Retrieved {len(filtered_vps)} connected servers from Ukraine")
            dump_json(filtered_vps, TP2_VPS_DATASET_CORRECTION)
        else:
            logger.error("VP dataset empty")
            sys.exit(1)


def exo4_get_all_targets() -> None:
    """get all connected servers from RU
    hints: we can add parameters to requests using the keyword params
    hints : params is a python dictionary
    """
    logger.info("###############################################")
    logger.info("#  EXO4                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/probes/"

    # 1. set parameters
    params = {"country_code": "RU"}

    if not params:
        logger.error("you must set parameters")
        sys.exit(1)
    else:
        # 1. perform request to get all RIPE Atlas servers in Russia
        response = requests.get(url=base_url, params=params).json()

        # 2. filter servers so they all :
        #   - have connected status (check the response)
        #   - have an IPv4 address
        filtered_targets = []
        for target in response["results"]:
            if target["status"]["name"] == "Connected":
                if target["address_v4"]:
                    filtered_targets.append(target)

        if filtered_targets:
            logger.info(
                f"Retrieved {len(filtered_targets)} connected servers from Russia"
            )
            dump_json(filtered_targets, TP2_TARGETS_DATASET_CORRECTION)
        else:
            logger.error("Target dataset empty")
            sys.exit(1)


def exo5_perform_measurement(
    target: dict,
    vp: dict,
    port: int,
    protocol: str,
    measurement_type: str,
    output_file_path: Path,
) -> int:
    """perform a traceroute from one vp in UA towards one server in RU"""
    logger.info("###############################################")
    logger.info("#  EXO5                                       #")
    logger.info("###############################################")

    ripe_credentials = get_ripe_atlas_credentials()

    if not ripe_credentials:
        raise RuntimeError(
            "set .env file at the root dir of the project with correct credentials"
        )

    base_url = f"https://atlas.ripe.net/api/v2/measurements/?key={ripe_credentials['secret_key']}"

    logger.info(
        f"Performing traceroute measurement from {vp['address_v4']} to {target['address_v4']}"
    )

    json_params = {
        "definitions": [
            {
                "target": target["address_v4"],
                "af": 4,
                "packets": 3,
                "size": 48,
                "tags": ["netmethr"],
                "description": f"Netmet",
                "resolve_on_probe": False,
                "skip_dns_check": True,
                "include_probe_id": False,
                "port": port,
                "type": measurement_type,
                "protocol": protocol,
            },
        ],
        "probes": [{"value": vp["id"], "type": "probes", "requested": 1}],
        "is_oneoff": True,
        "bill_to": ripe_credentials["username"],
    }

    response = requests.post(url=base_url, json=json_params).json()

    logger.info(response)

    measurement = {
        "measurement_id": response["measurements"],
        "measurement_description": json_params,
    }

    logger.info(f"measurement uuid (for retrieval): {response['measurements']}")

    insert_json(measurement, output_file_path)

    return measurement_id


if __name__ == "__main__":
    # comment methods you do not want to exec
    # (or uncomment otherwise)
    measurement_id = 60335345
    """exo1_get_a_measurement(
        measurement_id,
        output_file_path=TP2_RESULTS_PATH / "results_exo1_correction.json",
    )

    exo2_get_a_measurement_result(
        measurement_id,
        output_file_path=TP2_RESULTS_PATH / "results_exo2_correction.json",
    )

    exo3_get_all_vps()

    exo4_get_all_targets()"""

    """vp, target = get_one_vp_one_target_random()
    port = 80
    protocol = "ICMP"
    measurement_type = "traceroute"
    exo5_perform_measurement(
        target={'address_v4': '62.205.157.197', 'address_v6': '2a01:d0:0:23:220:4aff:fec5:589e', 'asn_v4': 29632, 'asn_v6': 29632, 'country_code': 'UA', 'description': 'NetAssist AS29632', 'first_connected': 1309789148, 'geometry': {'type': 'Point', 'coordinates': [30.5115, 50.4415]}, 'id': 699, 'is_anchor': False, 'is_public': True, 'last_connected': 1696317580, 'prefix_v4': '62.205.144.0/20', 'prefix_v6': '2a01:d0::/32', 'status': {'id': 1, 'name': 'Connected', 'since': '2023-10-02T00:10:25Z'}, 'status_since': 1696205425, 'tags': [{'name': 'Fibre', 'slug': 'fibre'}, {'name': 'Datacentre', 'slug': 'datacentre'}, {'name': 'dual-stack', 'slug': 'dual-stack'}, {'name': 'IPv4', 'slug': 'ipv4'}, {'name': 'IPv6', 'slug': 'ipv6'}, {'name': 'Multihomed', 'slug': 'multihomed'}, {'name': 'system: V1', 'slug': 'system-v1'}, {'name': 'system: Resolves A Correctly', 'slug': 'system-resolves-a-correctly'}, {'name': 'system: Resolves AAAA Correctly', 'slug': 'system-resolves-aaaa-correctly'}, {'name': 'system: IPv4 Works', 'slug': 'system-ipv4-works'}, {'name': 'system: IPv6 Works', 'slug': 'system-ipv6-works'}, {'name': 'system: IPv4 Capable', 'slug': 'system-ipv4-capable'}, {'name': 'system: IPv6 Capable', 'slug': 'system-ipv6-capable'}, {'name': 'system: IPv4 Stable 30d', 'slug': 'system-ipv4-stable-30d'}, {'name': 'system: IPv4 Stable 90d', 'slug': 'system-ipv4-stable-90d'}, {'name': 'system: IPv4 Stable 1d', 'slug': 'system-ipv4-stable-1d'}], 'total_uptime': 371163962, 'type': 'Probe'},
        vp={'address_v4': '178.252.197.138', 'address_v6': None, 'asn_v4': 24689, 'asn_v6': None, 'country_code': 'RU', 'description': 'JSC Rosintel', 'first_connected': 1311747023, 'geometry': {'type': 'Point', 'coordinates': [38.1785, 54.0775]}, 'id': 621, 'is_anchor': False, 'is_public': True, 'last_connected': 1696317400, 'prefix_v4': '178.252.197.0/24', 'prefix_v6': None, 'status': {'id': 1, 'name': 'Connected', 'since': '2023-09-29T02:09:37Z'}, 'status_since': 1695953377, 'tags': [{'name': 'No NAT', 'slug': 'no-nat'}, {'name': 'system: V1', 'slug': 'system-v1'}, {'name': 'system: Resolves A Correctly', 'slug': 'system-resolves-a-correctly'}, {'name': 'system: Resolves AAAA Correctly', 'slug': 'system-resolves-aaaa-correctly'}, {'name': 'system: IPv4 Works', 'slug': 'system-ipv4-works'}, {'name': 'system: IPv4 Capable', 'slug': 'system-ipv4-capable'}], 'total_uptime': 356032380, 'type': 'Probe'},
        port=port,
        protocol=protocol,
        measurement_type=measurement_type,
        output_file_path=TP2_RESULTS_PATH / "exo5_test_BA.json",
    )"""

    # On your own, make a measurement with the same target and same vp but:
    #   - change port number with ICMP
    #   - make one measurement with UDP
    # analyze the results

    measurement_ids = [61135433, 61135446]
    for id in measurement_ids:
        exo2_get_a_measurement_result(
            id, output_file_path=TP2_RESULTS_PATH / f"exo6_{id}.json"
        )
