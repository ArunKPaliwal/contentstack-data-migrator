import json
import os

import requests

import config
import utils


def content_type(uids):
    utils.log('content_type sync START', verbose=True)

    if uids is None:
        print('Please provide uids')
        utils.log('content_type sync END', verbose=True)
        return

    extensionsMap = {}
    with open('./data/mapping/extensions.json') as f:
        extensionsMap = json.load(f)  # Map of extension uids

    def updateCTinDst(ct, ctData):
        for schema in ctData['content_type']['schema']:
            if 'extension_uid' in schema:
                schema['extension_uid'] = extensionsMap[schema['extension_uid']]
        return requests.put(config.config['hostCM'] + '/content_types/' + ct, headers=config.destinationHeaders, json=ctData)

    def createCTinDst(ct, ctData):
        for schema in ctData['content_type']['schema']:
            if 'extension_uid' in schema:
                schema['extension_uid'] = extensionsMap[schema['extension_uid']]
        return requests.post(config.config['hostCM'] + '/content_types', headers=config.destinationHeaders, json=ctData)

    for uid in uids:
        ctDataSrc = requests.get(config.config['hostCM'] + '/content_types/' + uid, headers=config.sourceHeaders).json()
        if 'errors' in ctDataSrc:
            continue
        ctDst = requests.get(config.config['hostCM'] + '/content_types/' + uid, headers=config.destinationHeaders)
        if ctDst.status_code == 200:
            if ctDataSrc['content_type']['updated_at'] > ctDst.json()['content_type']['updated_at']:
                res = updateCTinDst(uid, ctDataSrc)
                if 'errors' in res:
                    print('Reference Error')
                    continue
                utils.log(f"content_type: '{uid}' UPDATED;   currVersion: {res.json()['content_type']['_version']}")
        else:
            res = createCTinDst(uid, ctDataSrc)
            if 'errors' in res:
                print('Reference Error')
                continue
            print(res.json())
            utils.log(f"content_type: '{uid}' CREATED;   currVersion: {res.json()['content_type']['_version']}")


    utils.log('content_type sync END', verbose=True)

def content_types():
    utils.log('content_types sync START', verbose=True)
    publishedContentTypeUID = []  # Will store list of all content types that MAY requires update/create in destination stack.
    extensionsMap = {}

    with open('./data/published/content_types.json') as f:
        publishedContentTypeUID = json.load(f)['content_type_uid']

    with open('./data/mapping/extensions.json') as f:
        extensionsMap = json.load(f)  # Map of extension uids

    try:
        os.makedirs('./data/content_types/')
    except FileExistsError:
        pass

    contentTypesWithRef = {}  # Map of content_types with all the referenced content_types

    while len(publishedContentTypeUID) != 0:
        top = publishedContentTypeUID.pop(0)
        if top not in contentTypesWithRef:
            getSingleContentTypeSrc = requests.get(config.config['hostCM'] + '/content_types/' + top, headers=config.sourceHeaders).json()
            getSingleContentTypeSrc['content_type'].pop('DEFAULT_ACL')
            getSingleContentTypeSrc['content_type'].pop('SYS_ACL')
            with open('./data/content_types/' + top + '.json', 'w') as f:
                f.write(json.dumps(getSingleContentTypeSrc, indent=4))

            flag = True
            for schema in getSingleContentTypeSrc['content_type']['schema']:
                if schema['data_type'] == 'reference':
                    contentTypesWithRef[top] = schema['reference_to']
                    flag = False
                    for ct in schema['reference_to']:
                        publishedContentTypeUID.append(ct)
            if flag:
                contentTypesWithRef[top] = []

    contentTypes = utils.topoSort(contentTypesWithRef)

    def updateCTinDst(ct):
        with open('./data/content_types/' + ct + '.json') as f:
            ctData = json.load(f)
            for schema in ctData['content_type']['schema']:
                if 'extension_uid' in schema:
                    schema['extension_uid'] = extensionsMap[schema['extension_uid']]
            return requests.put(config.config['hostCM'] + '/content_types/' + ct, headers=config.destinationHeaders, json=ctData)

    def createCTinDst(ct):
        with open('./data/content_types/' + ct + '.json') as f:
            ctData = json.load(f)
            for schema in ctData['content_type']['schema']:
                if 'extension_uid' in schema:
                    schema['extension_uid'] = extensionsMap[schema['extension_uid']]
            return requests.post(config.config['hostCM'] + '/content_types', headers=config.destinationHeaders, json=ctData)

    updateCTList = set()
    createCTList = set()

    for ct in contentTypes:
        ctSrcData = {}
        with open('./data/content_types/' + ct + '.json') as f:
            ctSrcData = json.load(f)

        getSingleContentTypeDst = requests.get(config.config['hostCM'] + '/content_types/' + ct, headers=config.destinationHeaders)
        ctDstData = getSingleContentTypeDst.json()

        if getSingleContentTypeDst.status_code == 200:
            if ctSrcData['content_type']['updated_at'] > ctDstData['content_type']['updated_at']:
                updateCTList.add(ct)
        else:
            createCTList.add(ct)

    f1 = utils.listChanges(updateCTList, name='content_types', action='updated')
    f2 = utils.listChanges(createCTList, name='content_types', action='created')

    if not config.list_only:
        if f1 or f2:
            utils.confirmChanges()
        for ct in contentTypes:
            if ct in updateCTList:
                res = updateCTinDst(ct)
                utils.log(f"content_type: '{ct}' UPDATED;   currVersion: {res.json()['content_type']['_version']}")
            elif ct in createCTList:
                res = createCTinDst(ct)
                utils.log(f"content_type: '{ct}' CREATED;   currVersion: {res.json()['content_type']['_version']}")

    utils.log('content_types sync END', verbose=True)
