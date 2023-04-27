from Jira.apis.base import JiraAPI
from Jira.templates.bot_comment import generate_bot_message


def add_comment(comment_type: str, key: str, data: dict) -> None:
    """ Add comment to specific Jira issue
    """
    jira_api = JiraAPI()

    my_content = [{
        'type': 'paragraph',
        'content': [
            {
                'type': 'text',
                'text': 'Jenkins Job: '
            },
            {
                'type': 'text',
                'text': data['jenkins_job_link'],
                'marks': [
                    {
                        'type': 'link',
                        'attrs': {
                            'href': data['jenkins_job_link']
                        }
                    }
                ]
            }
        ]
    }]

    comment_content = generate_bot_message(
        panel_type=comment_type,
        title='Transfer Hardware {}'.format(
            'Successful' if comment_type == 'success' else 'Failed'
        ),
        content=my_content
    )
    jira_api.add_comment_to_issue(
        keyOrID=key, comment_data=comment_content)
