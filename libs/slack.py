import os
import slack

sc = slack.WebClient(token=os.environ.get('SLACK_API_TOKEN'))


def post_customer(text):
    return post(text, ':boy:', 'Customer')


def post_agent(text):
    return post(text, ':girl:', 'Agent')


def post(text, icon_emoji, username):
    response = sc.chat_postMessage(
        channel=os.environ.get('SLACK_POST_CHANNEL'),
        icon_emoji=icon_emoji,
        username=username,
        text=text,
    )
    return response['ok'] if 'ok' in response else False
