'''
    TELOPS Jira Board Handler
'''

import json

from Jira.apis.base import JiraAPI, get_jira_members


def create_send_dut_to_cert_card_in_telops(
        cqt_card: str,
        reporter: str,
        data: list
        ) -> None:
    """ Create card to TELOPS board for contractor using, the type of card is
        "DUT Send To Cert"

        @param:cqt_card, the key of the original card in CQT board.
            e.g. CQT-1234

        @param:reporter, the launchpad ID of someone QA.

        @param:data, a list contains CID information.
            e.g
                [
                    {
                        'CID': '202303-12345',
                        'Location': ''
                    },
                ]
    """
    qa_members = get_jira_members()
    issue_updates = []  # Put tasks in this list

    telops_jira_api = JiraAPI(
        path_of_jira_board_conf='./configs',
        jira_board_conf='jira_telops.json'
    )

    for d in data:
        # Template of "fields" payload in Jira's request
        fields = telops_jira_api.create_jira_fields_template(
            task_type='DUT_Send_To_Cert')

        # Assign Summary
        fields['summary'] = 'Send CID#{} to Cert Lab'.format(d['cid'])

        # Assign Reporter
        fields['reporter']['id'] = qa_members[reporter]['jira_uid']

        # Link task back to CQT task
        update_link = telops_jira_api.create_link_issue_content(
            target_issues=[{'key': cqt_card}])

        issue_updates.append({'fields': fields, 'update': update_link})

    response = telops_jira_api.create_issues(
        payload={'issueUpdates': issue_updates})
    if not response.ok:
        print('*' * 50)
        print(json.dumps(issue_updates, indent=2))
        raise Exception(
            'Error: Failed to create card to TELOPS board',
            'Reason: {}'.format(response.text)
        )
    print('Created the following cards to TELOPS board successfully')
    print(json.dumps(response.json(), indent=2))