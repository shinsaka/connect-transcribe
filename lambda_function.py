import json
import re
import boto3
from libs import slack
from libs import transcribe_utils


def handler(event, context):
    print(json.dumps(event))
    for rec in event['Records']:
        if is_wav(rec):
            start_transcription_job(rec)
        if is_json(rec):
            contexts = get_transcribed_contexts(rec)
            post_messages(contexts)

    return {}

def is_wav(rec):
    return rec['s3']['object']['key'].endswith('.wav')


def is_json(rec):
    return rec['s3']['object']['key'].endswith('.wav.json')


def start_transcription_job(rec):
    """
    submit transcritption job
    """
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

def get_transcribed_contexts(rec):
    """
    return: iterator element=(start_time, ch_name, content )
    """
    s3 = boto3.resource('s3')
    obj_response = s3.Object(rec['s3']['bucket']['name'], rec['s3']['object']['key']).get()
    return transcribe_utils.get_transcribed_contexts(json.load(obj_response['Body']))


def post_messages(contexts):
    for ch_data in contexts:
        if ch_data[1] == 'ch_0':
            slack.post_customer(ch_data[2])
        else:
            slack.post_agent(ch_data[2])
