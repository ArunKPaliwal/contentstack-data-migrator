import json
import os

import requests

import config
import utils


def initial_sync():
    utils.log('initial_sync START', verbose=True)

    publishedContentTypeUID = set()  # Stores published content types in curr env and after specified date
    publishedEntries = []  # Stores published entries in curr env and after specified date
    publishedAssets = {}  # Stores published assets in curr env and after specified date

    initialSyncSrc = requests.get(config.config['hostCD'] + '/stacks/sync?init=true&environment=' + config.config[
        'source_environment'] + '&start_from=' + config.from_date, headers=config.deliveryHeaders)
    res = initialSyncSrc.json()

    for item in res['items']:
        if item['content_type_uid'] != 'sys_assets':
            publishedContentTypeUID.add(item['content_type_uid'])
            publishedEntries.append({'uid': item['data']['uid'], '_content_type_uid': item['content_type_uid']})
        else:
            asset = {'title': item['data']['title'], 'content_type': item['data']['content_type'],
                     'filename': item['data']['filename'], 'parent_uid': 'null'}
            if 'parent_uid' in item['data']:
                asset['parent_uid'] = item['data']['parent_uid']
            publishedAssets[item['data']['uid']] = asset

    while 'pagination_token' in res:
        pgToken = res['pagination_token']
        res = requests.get(config.config['hostCD'] + '/stacks/sync?pagination_token=' + pgToken,
                           headers=config.deliveryHeaders).json()
        for item in res['items']:
            if item['content_type_uid'] != 'sys_assets':
                publishedContentTypeUID.add(item['content_type_uid'])
                publishedEntries.append({'uid': item['data']['uid'], '_content_type_uid': item['content_type_uid']})
            else:
                asset = {'title': item['data']['title'], 'content_type': item['data']['content_type'],
                         'filename': item['data']['filename'], 'parent_uid': 'null'}
                if 'parent_uid' in item['data']:
                    asset['parent_uid'] = item['data']['parent_uid']
                publishedAssets[item['data']['uid']] = asset

    try:
        os.makedirs('./data/published')
    except FileExistsError:
        pass

    with open('./data/published/assets.json', 'w') as f:
        f.write(json.dumps(publishedAssets, indent=4))

    with open('./data/published/content_types.json', 'w') as f:
        f.write(json.dumps({'content_type_uid': list(publishedContentTypeUID)}, indent=4))

    with open('./data/published/entries.json', 'w') as f:
        f.write(json.dumps({'entries': list(publishedEntries)}, indent=4))

    extensionsMap = {}
    getAllExtSrc = requests.get(config.config['hostCM'] + '/extensions', headers=config.sourceHeaders).json()
    getAllExtDst = requests.get(config.config['hostCM'] + '/extensions', headers=config.destinationHeaders).json()
    for extSrc in getAllExtSrc['extensions']:
        for extDst in getAllExtDst['extensions']:
            if extSrc['title'] == extDst['title']:
                extensionsMap[extSrc['uid']] = extDst['uid']

    try:
        os.makedirs('./data/mapping')
    except FileExistsError:
        pass

    with open('./data/mapping/extensions.json', 'w') as f:
        f.write(json.dumps(extensionsMap, indent=4))

    utils.log('initial_sync END', verbose=True)
