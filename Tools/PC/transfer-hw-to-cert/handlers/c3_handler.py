import os

from C3.apis.base import C3API, TaipeiLocation
from utils.common import parse_location


def init_c3_api() -> object:
    c3 = C3API() if os.path.exists('./configs/production_c3.txt') \
        else C3API(
        base_url='https://certification.staging.canonical.com/api/v1/hardware')

    return c3


def update_duts_info_on_c3(data: list[dict], new_holder: str):
    """ Update DUTS' information on C3 webstie

        Currently, we update the holder and location
    """
    c3 = init_c3_api()

    for dut in data:
        payload = {
            'holder': new_holder,
            'location': TaipeiLocation[
                parse_location(dut['location'])['Lab'].replace('-', '_')].value
        }
        print('Updating {}'.format(dut['cid']))
        res = c3.update_dut_by_cid(cid=dut['cid'], payload=payload)
        if res.status_code < 200 or res.status_code > 299:
            raise Exception('Error: update failed')
