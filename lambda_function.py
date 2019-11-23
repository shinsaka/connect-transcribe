import json
import re
import boto3
from libs import slack


def handler(event, context):
    print(json.dumps(event))
    for rec in event['Records']:
        if is_wav(rec):
            start_transcription_job(rec)
        if is_json(rec):
            for ch_data in parse_transcribed_json(rec):
                if ch_data[1] == 'ch_0':
                    slack.post_customer(ch_data[2])
                else:
                    slack.post_agent(ch_data[2])

    return {}

def is_wav(rec):
    return rec['s3']['object']['key'].endswith('.wav')


def is_json(rec):
    return rec['s3']['object']['key'].endswith('.wav.json')


def start_transcription_job(rec):
    client = boto3.client('transcribe')
    return client.start_transcription_job(
        TranscriptionJobName=re.sub(r'[^-._a-zA-Z0-9]', '_', rec['s3']['object']['key']),
        LanguageCode='ja-JP',
        MediaSampleRateHertz=8000,
        MediaFormat='wav',
        Media={
            'MediaFileUri': 'https://s3.{aws_region}.amazonaws.com/{bucket_name}/{object_key}'.format(
                aws_region=rec['awsRegion'],
                bucket_name=rec['s3']['bucket']['name'],
                object_key=rec['s3']['object']['key']
            )
        },
        OutputBucketName=rec['s3']['bucket']['name'],
        Settings={
            'ChannelIdentification': True
        }
    )

def parse_transcribed_json(rec):
    """
    return: iterator  element=(start_time, ch_name, content )
    """
    ch_name = None
    start_time = 0
    content = ''
    for item in sorted(_get_channel_items(rec)):
        if ch_name is None or ch_name != item[1]:
            if content:
                yield (start_time, ch_name, content)
            start_time = item[0]
            ch_name = item[1]
            content = item[2]
        else:
            content += item[2]

    if content:
        yield (start_time, ch_name, content)


def _get_channel_items(rec):
    s3 = boto3.resource('s3')
    obj_response = s3.Object(rec['s3']['bucket']['name'], rec['s3']['object']['key']).get()

    response_json = json.load(obj_response['Body'])

    for channel in response_json['results']['channel_labels']['channels']:
        for item in channel['items']:
            yield (
                float(item['start_time']),
                channel['channel_label'],
                ''.join([alt['content'] for alt in item['alternatives']])
            )


rec={'s3':{'bucket':{'name': 'shinsaka-connect'},'object':{'key':'1.wav.json'}}}

for c in parse_transcribed_json(rec):
    if c[1] == 'ch_0':
        slack.post_customer(c[2])
    else:
        slack.post_agent(c[2])
