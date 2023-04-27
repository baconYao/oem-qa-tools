from C3.apis.base import C3API, TaipeiLocation
from utils.common import parse_location


def update_duts_info_on_c3(data: list[dict], new_holder: str):
    """ Update DUTS' information on C3 webstie

        Currently, we update the holder and location
    """
    # FIXME: no staging_site here
    staging_site = \
        'https://certification.staging.canonical.com/api/v1/hardware'
    c3 = C3API(base_url=staging_site)

    for dut in data:
        # print(dut['cid'], dut['location'])
        # print(parse_location(dut['location'])['Lab'].replace('-', '_'))
        payload = {
            'holder': new_holder,
            'location': TaipeiLocation[
                parse_location(dut['location'])['Lab'].replace('-', '_')].value
        }
        print('Updating {}'.format(dut['cid']))
        c3.update_dut_by_cid(cid=dut['cid'], payload=payload)
