import json
import os

import requests

import config
import utils


def entry(uids, ctList):
    utils.log('entry sync START', verbose=True)

    if uids is None or ctList is None or len(uids) != len(ctList):
        print('Please provide valid uids')
        utils.log('entry sync END', verbose=True)
        return

    entriesMap = {}
    assetsMap = {}
    with open('./data/mapping/entries.json') as f:
        entriesMap = json.load(f)
    with open('./data/mapping/assets.json') as f:
        assetsMap = json.load(f)

    def updateEntryDst(uid, ct):
        file_field_uid = []
        file_field_uid_multiple = []
        ctData = requests.get(config.config['hostCM'] + '/content_types/'+ct, headers=config.sourceHeaders).json()
        if 'errors' in ctData:
            return False
        for schema in ctData['content_type']['schema']:
            if schema['data_type'] == 'file':
                if schema['multiple']:
                    file_field_uid_multiple.append(schema['uid'])
                else:
                    file_field_uid.append(schema['uid'])
        entryData = requests.get(config.config['hostCM'] + '/content_types/' + ct + '/entries/' + uid + '?environment=' + config.config['source_environment'], headers=config.sourceHeaders).json()
        if 'errors' in ctData:
            return False
        for ffUID in file_field_uid:
            if ffUID in entryData['entry']:
                entryData['entry'][ffUID] = assetsMap[entryData['entry'][ffUID]['uid']]

        for ffUID in file_field_uid_multiple:
            fileList = []
            if ffUID in entryData['entry']:
                for file in entryData['entry'][ffUID]:
                    fileList.append(assetsMap[file['uid']])
            entryData['entry'][ffUID] = fileList

        if 'reference' in entryData['entry']:
            for ref in entryData['entry']['reference']:
                try:
                    ref['uid'] = entriesMap[ref['uid']]
                except Exception:
                    pass

        res = requests.put(config.config['hostCM'] + '/content_types/' + ct + '/entries/' + entriesMap[uid], headers=config.destinationHeaders, json=entryData)
        return res

    def createEntryDst(uid, ct):
        file_field_uid = []
        file_field_uid_multiple = []
        ctData = requests.get(config.config['hostCM'] + '/content_types/'+ct, headers=config.sourceHeaders).json()
        if 'errors' in ctData:
            return False
        for schema in ctData['content_type']['schema']:
            if schema['data_type'] == 'file':
                if schema['multiple']:
                    file_field_uid_multiple.append(schema['uid'])
                else:
                    file_field_uid.append(schema['uid'])
        entryData = requests.get(config.config['hostCM'] + '/content_types/' + ct + '/entries/' + uid + '?environment=' + config.config['source_environment'], headers=config.sourceHeaders).json()
        if 'errors' in ctData:
            return False
        for ffUID in file_field_uid:
            if ffUID in entryData['entry']:
                entryData['entry'][ffUID] = assetsMap[entryData['entry'][ffUID]['uid']]

        for ffUID in file_field_uid_multiple:
            fileList = []
            if ffUID in entryData['entry']:
                for file in entryData['entry'][ffUID]:
                    fileList.append(assetsMap[file['uid']])
            entryData['entry'][ffUID] = fileList

        if 'reference' in entryData['entry']:
            for ref in entryData['entry']['reference']:
                try:
                    ref['uid'] = entriesMap[ref['uid']]
                except Exception:
                    pass

        res = requests.post(config.config['hostCM'] + '/content_types/' + ct + '/entries', headers=config.destinationHeaders, json=entryData)
        if 'entry' in res.json():
            entriesMap[entry['uid']] = res.json()['entry']['uid']
        return res

    for i in range(len(uids)):
        if uids[i] in entriesMap:
            res = updateEntryDst(uids[i], ctList[i])
            if not res or 'errors' in res.json():
                print('Reference error')
                continue
            utils.log(f"entry: '{res.json()['entry']['title']}'({res.json()['entry']['uid']}) UPDATED;   currVersion: {res.json()['entry']['_version']}")
        else:
            res = createEntryDst(uids[i], ctList[i])
            if not res or 'errors' in res.json():
                print('Reference error or Title not unique error')
                continue
            utils.log(f"entry: '{res.json()['entry']['title']}' CREATED :: mapping {entry['uid']} -> {res.json()['entry']['uid']};   currVersion: {res.json()['entry']['_version']}")

    with open('./data/mapping/entries.json', 'w') as f:
            f.write(json.dumps(entriesMap, indent=4))

    utils.log('entry sync END', verbose=True)

def entries():
    utils.log('entries sync START', verbose=True)

    publishedEntries = []
    entriesMap = {}
    assetsMap = {}
    with open('./data/published/entries.json') as f:
        publishedEntries = json.load(f)['entries']
    with open('./data/mapping/entries.json') as f:
        entriesMap = json.load(f)
    with open('./data/mapping/assets.json') as f:
        assetsMap = json.load(f)
    try:
        os.makedirs('./data/entries/')
    except FileExistsError:
        pass

    allEntries = {}

    entriesWithRefs = {}
    for entry in publishedEntries:
        entriesWithRefs[entry['uid']] = entry['_content_type_uid']

    while len(publishedEntries) != 0:
        top = publishedEntries.pop(0)
        if top['uid'] not in allEntries:
            getSingleEntrySrc = requests.get(config.config['hostCM'] + '/content_types/' + top['_content_type_uid'] + '/entries/' + top['uid'] + '?environment=' + config.config['source_environment'], headers=config.sourceHeaders).json()
            with open('./data/entries/' + top['_content_type_uid'] + '_' + top['uid'] + '.json', 'w') as f:
                f.write(json.dumps(getSingleEntrySrc, indent=4))
            if 'reference' in getSingleEntrySrc['entry']:
                children = []
                for ref in getSingleEntrySrc['entry']['reference']:
                    children.append(ref['uid'])
                    publishedEntries.append(ref)
                    entriesWithRefs[ref['uid']] = ref['_content_type_uid']
                allEntries[top['uid']] = children
            else:
                allEntries[top['uid']] = []

    entriesUID = utils.topoSort(allEntries)

    sortedEntries = []
    for uid in entriesUID:
        sortedEntries.append({'uid': uid, '_content_type_uid': entriesWithRefs[uid]})

    def checkIfUpdateNeeded(entry):
        srcEntry = {}
        with open('./data/entries/' + entry['_content_type_uid'] + '_' + entry['uid'] + '.json') as f:
            srcEntry = json.load(f)
        dstEntry = requests.get(config.config['hostCM'] + '/content_types/' + entry['_content_type_uid'] + '/entries/' + entriesMap[entry['uid']] + '?environment=' + config.config['destination_environment'], headers=config.destinationHeaders).json()
        if 'errors' in dstEntry:
            return True
        if srcEntry['entry']['updated_at'] > dstEntry['entry']['updated_at'] or srcEntry['entry']['updated_at'] > \
                dstEntry['entry']['publish_details']['time']:
            return True
        elif srcEntry['entry']['publish_details']['time'] > dstEntry['entry']['publish_details']['time']:  # if entry have rolled backed to previous version in src stack then update time will not change but publish time will changes.
            return True
        else:
            return False

    def createEntryDst(entry):
        file_field_uid = []
        file_field_uid_multiple = []
        with open('./data/content_types/' + entry['_content_type_uid'] + '.json') as f:
            ctData = json.load(f)
            for schema in ctData['content_type']['schema']:
                if schema['data_type'] == 'file':
                    if schema['multiple']:
                        file_field_uid_multiple.append(schema['uid'])
                    else:
                        file_field_uid.append(schema['uid'])
        with open('./data/entries/' + entry['_content_type_uid'] + '_' + entry['uid'] + '.json') as f:
            entryData = json.load(f)
            for ffUID in file_field_uid:
                if ffUID in entryData['entry']:
                    entryData['entry'][ffUID] = assetsMap[entryData['entry'][ffUID]['uid']]
            for ffUID in file_field_uid_multiple:
                fileList = []
                if ffUID in entryData['entry']:
                    for file in entryData['entry'][ffUID]:
                        fileList.append(assetsMap[file['uid']])
                entryData['entry'][ffUID] = fileList

            if 'reference' in entryData['entry']:
                for ref in entryData['entry']['reference']:
                    try:
                        ref['uid'] = entriesMap[ref['uid']]
                    except Exception:
                        pass

            res = requests.post(config.config['hostCM'] + '/content_types/' + entry['_content_type_uid'] + '/entries',
                                headers=config.destinationHeaders, json=entryData)
            if 'entry' in res.json():
                entriesMap[entry['uid']] = res.json()['entry']['uid']
            return res

    def updateEntryDst(entry):
        file_field_uid = []
        file_field_uid_multiple = []

        with open('./data/content_types/' + entry['_content_type_uid'] + '.json') as f:
            ctData = json.load(f)
            for schema in ctData['content_type']['schema']:
                if schema['data_type'] == 'file':
                    if schema['multiple']:
                        file_field_uid_multiple.append(schema['uid'])
                    else:
                        file_field_uid.append(schema['uid'])

        with open('./data/entries/' + entry['_content_type_uid'] + '_' + entry['uid'] + '.json') as f:
            entryData = json.load(f)
            for ffUID in file_field_uid:
                if ffUID in entryData['entry']:
                    entryData['entry'][ffUID] = assetsMap[entryData['entry'][ffUID]['uid']]

            for ffUID in file_field_uid_multiple:
                fileList = []
                if ffUID in entryData['entry']:
                    for file in entryData['entry'][ffUID]:
                        fileList.append(assetsMap[file['uid']])
                entryData['entry'][ffUID] = fileList

            if 'reference' in entryData['entry']:
                for ref in entryData['entry']['reference']:
                    try:
                        ref['uid'] = entriesMap[ref['uid']]
                    except Exception:
                        pass

            res = requests.put(
                config.config['hostCM'] + '/content_types/' + entry['_content_type_uid'] + '/entries/' + entriesMap[
                    entry['uid']], headers=config.destinationHeaders, json=entryData)
            return res

    updateEntryList = {}
    createEntryList = {}
    for entry in sortedEntries:
        if entry['uid'] in entriesMap:
            if checkIfUpdateNeeded(entry):
                updateEntryList[entry['uid']] = entry
        else:
            createEntryList[entry['uid']] = entry

    f1 = utils.listChanges(list(updateEntryList.values()), 'entries', 'updated')
    f2 = utils.listChanges(list(createEntryList.values()), 'entries', 'created')

    if not config.list_only:
        if f1 or f2:
            utils.confirmChanges()
        for entry in sortedEntries:
            if entry['uid'] in updateEntryList:
                res = updateEntryDst(updateEntryList[entry['uid']])
                utils.log(f"entry: '{res.json()['entry']['title']}'({res.json()['entry']['uid']}) UPDATED;   currVersion: {res.json()['entry']['_version']}")
            elif entry['uid'] in createEntryList:
                res = createEntryDst(createEntryList[entry['uid']])
                # if 'errors' in res.json():
                utils.log(f"entry: '{res.json()['entry']['title']}' CREATED :: mapping {entry['uid']} -> {res.json()['entry']['uid']};   currVersion: {res.json()['entry']['_version']}")

        with open('./data/mapping/entries.json', 'w') as f:
            f.write(json.dumps(entriesMap, indent=4))

    utils.log('entries sync END', verbose=True)