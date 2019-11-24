def get_transcribed_contexts(transcribed_dict):
    # iterator for sorted contexts
    ch_name = None
    start_time = 0
    content = ''
    for item in sorted(_get_channel_items(transcribed_dict)):
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


def _get_channel_items(transcribed_dict):
    # iterator for channel items from transcribed json
    for channel in transcribed_dict['results']['channel_labels']['channels']:
        for item in channel['items']:
            yield (
                float(item['start_time']),
                channel['channel_label'],
                ''.join([alt['content'] for alt in item['alternatives']])
            )
