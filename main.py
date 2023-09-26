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
        logger.info("using vps and targets from the correction")

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
    
    measurement_id = 38333397
    base_url = "https://atlas.ripe.net/api/v2/measurements/"

    ####################################################################
    # TODO: make an http request to RIPE API (using requests package)  #
    # to get measurement with measurement id : 38333397                #
    ####################################################################
    measurement_description: dict =  requests.get(f"{base_url}{measurement_id}/").json()

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
    measurement_id = 38333397

    base_url = "https://atlas.ripe.net/api/v2/measurements/"

    ####################################################################
    # TODO: make an http request to RIPE API (using requests package)  #
    # to get measurement results for measurement uuid 38333397         #
    ####################################################################

    # 1. get measurement description
    response = requests.get(f"{base_url}{measurement_id}/")

    if not response:
        logger.error("measurement description is empty")
        sys.exit(1)

    # 2. check measurement description to get measurement results url
    measurement_description = response.json()
    result_url = measurement_description.get("result")

    if not result_url:
        logger.error("result url empty")
        sys.exit(1)

    # 3. make the request to get measurement results
    results_response = requests.get(result_url)

    if not result_url:
        logger.error("Measurement results empty")
        sys.exit(1)

    # 4. just take the first result
    results = results_response.json()[0]

    logger.info("Results:")
    for key, val in results.items():
        logger.info(f"{key} : {val}")
    logger.info("\n")

    # 5. from measurement result, get:
    #   - the source address of the measurement
    #   - the destination address of the measurement
    #   - the type of the measurement
    src_addr = measurement_description.get("source")
    dst_addr = measurement_description.get("destination")
    measurement_type = measurement_description.get("type")

    logger.info(f"measurement source : {src_addr}")
    logger.info(f"measurement dst : {dst_addr}")
    logger.info(f"measurement type   : {measurement_type} \n")

    # 6. get actual measurement results
    traceroute = results.get("result")

    # 7. print the traceroute
    logger.info("Traceroute results")
    if traceroute:
        print_traceroute(traceroute)

        dump_json(results, output_file_path)

        return traceroute


def exo3_get_all_vps() -> None:
    """Get all connected servers from UA."""
    logger.info("###############################################")
    logger.info("#  EXO3                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/probes/"

    # 1. Set parameters (Define your parameters here)
    params = {
        "country_code": "UA",  # Add other required parameters as needed
        "status": "1",  # Assuming '1' means connected status, adjust as needed
        "is_public": "true",  # Assuming you want public servers, adjust as needed
    }

    if not params:
        logger.error("You must set parameters")
        sys.exit(1)
    else:
        # 2. Perform a request to get all RIPE Atlas servers in Ukraine
        response = requests.get(base_url, params=params)

        if not response:
            logger.error("Failed to fetch connected servers from Ukraine")
            sys.exit(1)

        # 3. Filter servers so they all have connected status and an IPv4 address (Define your filtering logic here)
        all_servers = response.json()

        if all_servers:
            logger.info(f"Retrieved {len(all_servers)} servers from Russia")
            # Dump the data to a file (Use your dump_json function)
            dump_json(all_servers, TP2_VPS_DATASET_CORRECTION)  # Replace with the appropriate file path
        else:
            logger.error("VP dataset is empty")
            sys.exit(1)
                 

def exo4_get_all_targets() -> None:
    """Get all connected servers from RU."""
    logger.info("###############################################")
    logger.info("#  EXO4                                       #")
    logger.info("###############################################")

    base_url = "https://atlas.ripe.net/api/v2/probes/"

    # 1. Set parameters (Define your parameters here)
    params = {
        "country_code": "RU",  # Add other required parameters as needed
        "is_public": "true",  # Assuming you want public servers, adjust as needed
    }

    if not params:
        logger.error("You must set parameters")
        sys.exit(1)
    else:
        # 2. Perform a request to get all RIPE Atlas servers in Russia
        response = requests.get(base_url, params=params)

        if not response:
            logger.error("Failed to fetch connected servers from Russia")
            sys.exit(1)

        # 3. Get all servers without specific filtering
        all_servers = response.json()

        if all_servers:
            logger.info(f"Retrieved {len(all_servers)} servers from Russia")
            # Dump the data to a file (Use your dump_json function)
            dump_json(all_servers, TP2_TARGETS_DATASET_CORRECTION)
        else:
            logger.error("Target dataset is empty")
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
                "description": "Netmet",
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
        output_file_path = TP2_RESULTS_PATH / "results_exo1_correction.json",
    )"""

    """exo2_get_a_measurement_result(
        measurement_id,
        output_file_path=TP2_RESULTS_PATH / "results_exo2_correction.json",
    )"""

    #exo3_get_all_vps()

    #exo4_get_all_targets()

    vp, target = get_one_vp_one_target_random()
    port = 34543
    protocol = "ICMP"
    measurement_type = "traceroute"
    exo5_perform_measurement(
        target=target,
        vp=vp,
        port=port,
        protocol=protocol,
        measurement_type=measurement_type,
        output_file_path=TP2_RESULTS_PATH / "results_exo5_correction.json",
    ) 

    # On your own, make a measurement with the same target and same vp but:
    #   - change port number with ICMP
    #   - make one measurement with UDP
    # analyze the results

    # measurement_ids = [60359913, 60359920, 60359932]

    """ for id in measurement_ids:
        exo2_get_a_measurement_result(
            id, output_file_path=TP2_RESULTS_PATH / f"exo6_correction_{id}.json"
        ) """
