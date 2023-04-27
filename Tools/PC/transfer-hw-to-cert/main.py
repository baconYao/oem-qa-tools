import json
from argparse import ArgumentParser

from jira_card_handler import get_candidate_duts
from cert_team_google_sheet_handler import update_cert_lab_google_sheet
from c3_handler import update_duts_info_on_c3
from notifier import add_comment


def register_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        '-k', '--key',
        help='The key string of specific Jira Card. e.g. CQT-2023',
        type=str,
        required=True
    )
    parser.add_argument(
        '-j', '--jenkins-job-link',
        help='The link of jenkins job.',
        type=str,
        default='http://<ip>/view/qa-services/job/qa-transfer-hw-to-cert-lab/',
    )
    parser.add_argument(
        '-c', '--c3-holder',
        help='The DUT holder on C3. Please feed the launchpad id',
        type=str,
        default='kevinyeh'
    )
    return parser.parse_args()


def main():
    args = register_arguments()

    key = args.key
    try:
        print('-' * 5 + 'Retrieving data from Jira Card' + '-' * 5)
        # Get data from specific Jira Card
        data = get_candidate_duts(key)
        print(json.dumps(data, indent=2))
        if data['invalid']:
            raise Exception(
                f'Error: found invalid record from Jira Card {key}')

        # Update Cert Lab Google Sheet
        gm_image_link = data['gm_image_link']
        for d in data['valid']:
            d['gm_image_link'] = gm_image_link

        print('-' * 5 + 'Updating Cert Lab Google Sheet' + '-' * 5)
        update_cert_lab_google_sheet(data['valid'])

        # Update DUT holder and location on C3
        print('-' * 5 + 'Updating C3' + '-' * 5)
        update_duts_info_on_c3(data=data['valid'], new_holder=args.c3_holder)

        #  notify: leave successful comment to Jira card
        add_comment(
            comment_type='success',
            key=key,
            data={
                'jenkins_job_link': args.jenkins_job_link
            }
        )
    except Exception:
        # notify: leave failed comment to Jira card
        add_comment(
            comment_type='error',
            key=key,
            data={
                'jenkins_job_link': args.jenkins_job_link
            }
        )
        raise


if __name__ == '__main__':
    main()
