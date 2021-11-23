import json
import os

import requests
from requests_toolbelt import MultipartEncoder

import config
import utils


def asset(uids):
    utils.log('asset sync START', verbose=True)

    if uids is None:
        print('Please provide uids')
        utils.log('asset sync END', verbose=True)
        return

    assetsMap = {}  # Stores a map of assets in curr env and after specified date to assets in prod stack
    assetsDirMap = {}
    try:
        os.makedirs('./data/mapping')
    except FileExistsError:
        pass

    if os.path.isfile('./data/mapping/assets.json'):
        with open('./data/mapping/assets.json') as f:
            assetsMap = json.load(f)

    if os.path.isfile('./data/mapping/assetsDir.json'):
        with open('./data/mapping/assetsDir.json') as f:
            assetsDirMap = json.load(f)

    asset = {}

    def getAsset(uid):
        getAssetSrc = requests.get(config.config['hostCM'] + '/assets/' + uid, headers=config.sourceHeaders).json()
        if 'errors' in getAssetSrc:
            print('--Invalid UID')
            return True
        assetUrl = getAssetSrc['asset']['url']
        try:
            asset['title'] = getAssetSrc['asset']['title']
            asset['url'] = assetUrl
            asset['filename'] = getAssetSrc['asset']['filename']
            asset['content_type'] = getAssetSrc['asset']['content_type']
            asset['tags'] = getAssetSrc['asset']['tags']
            asset['parent_uid'] = getAssetSrc['asset']['parent_uid']
        except:
            pass
        fetchAsset(assetUrl, uid)
        return False

    def fetchAsset(url, uid):
        asset = requests.get(url, allow_redirects=True)
        try:
            os.makedirs('./data/assets/' + uid)
        except FileExistsError:
            pass
        with open('./data/assets/' + uid + '/' + url.split('/')[-1], 'wb') as f:
            f.write(asset.content)

    def pushAssetToProd(assetUIDSrc, asset):
        with open('./data/assets/' + assetUIDSrc + '/' + asset['filename'], 'rb') as f:
            dstParentUID = config.assetParentUID
            if asset['parent_uid'] in assetsDirMap:
                dstParentUID = assetsDirMap[asset['parent_uid']]

            data = MultipartEncoder(
                fields={
                    'asset[upload]': (asset['title'], f, asset['content_type']),
                    'asset[parent_uid]': dstParentUID,
                    'asset[title]': asset['title'],
                    'asset[tags]': ','.join(asset['tags'])
                }
            )
            headers = config.destinationHeaders.copy()
            headers['Content-Type'] = data.content_type
            return requests.post(config.config['hostCM'] + '/assets', headers=headers, data=data).json()
    for uid in uids:
        if uid not in assetsMap.keys():
            if getAsset(uid):
                continue
            res = pushAssetToProd(uid, asset)
            assetsMap[uid] = res['asset']['uid']
            utils.log(f"'{res['asset']['filename']}' CREATED :: mapping {uid} -> {res['asset']['uid']}")

    with open('./data/mapping/assets.json', 'w') as f:
            f.write(json.dumps(assetsMap, indent=4))

    utils.log('asset sync END', verbose=True)

def assets():
    utils.log('assets sync START', verbose=True)

    try:
        os.makedirs('./data/assets')
    except FileExistsError:
        pass

    def getAsset(uid):
        getAssetSrc = requests.get(config.config['hostCM'] + '/assets/' + uid, headers=config.sourceHeaders).json()
        assetUrl = getAssetSrc['asset']['url']
        try:
            publishedAssets[uid]['parent_uid'] = getAssetSrc['asset']['parent_uid']
            publishedAssets[uid]['description'] = getAssetSrc['asset']['description']
        except:
            publishedAssets[uid]['description'] = ''

        publishedAssets[uid]['tags'] = getAssetSrc['asset']['tags']
        fetchAsset(assetUrl, uid)

    def fetchAsset(url, uid):
        asset = requests.get(url, allow_redirects=True)
        try:
            os.makedirs('./data/assets/' + uid)
        except FileExistsError:
            pass
        with open('./data/assets/' + uid + '/' + url.split('/')[-1], 'wb') as f:
            f.write(asset.content)

    def pushAssetToProd(assetUIDSrc, asset):
        with open('./data/assets/' + assetUIDSrc + '/' + asset['filename'], 'rb') as f:
            dstParentUID = config.assetParentUID
            if asset['parent_uid'] in assetsDirMap:
                dstParentUID = assetsDirMap[asset['parent_uid']]

            data = MultipartEncoder(
                fields={
                    'asset[upload]': (asset['title'], f, asset['content_type']),
                    'asset[parent_uid]': dstParentUID,
                    'asset[title]': asset['title'],
                    'asset[tags]': ','.join(asset['tags'])
                }
            )
            headers = config.destinationHeaders.copy()
            headers['Content-Type'] = data.content_type
            return requests.post(config.config['hostCM'] + '/assets', headers=headers, data=data).json()

    assetsMap = {}  # Stores a map of assets in curr env and after specified date to assets in prod stack
    assetsDirMap = {}
    try:
        os.makedirs('./data/mapping')
    except FileExistsError:
        pass

    if os.path.isfile('./data/mapping/assets.json'):
        with open('./data/mapping/assets.json') as f:
            assetsMap = json.load(f)

    if os.path.isfile('./data/mapping/assetsDir.json'):
        with open('./data/mapping/assetsDir.json') as f:
            assetsDirMap = json.load(f)

    publishedAssets = {}
    with open('./data/published/assets.json') as f:
        publishedAssets = json.load(f)

    oldAssets = [key for key in publishedAssets if key in assetsMap]

    for key in oldAssets: publishedAssets.pop(key)

    assetsList = []
    for uid in publishedAssets.keys():
        assetsList.append(f"{publishedAssets[uid]['filename']} ({uid})")

    f = utils.listChanges(assetsList, name='assets', action='added')

    if not config.list_only:
        if f:
            utils.confirmChanges()
        for assetUID in publishedAssets.keys():
            if assetUID in assetsMap.keys():
                continue
            else:
                getAsset(assetUID)
                res = pushAssetToProd(assetUID, publishedAssets[assetUID])
                assetsMap[assetUID] = res['asset']['uid']
                utils.log(f"'{res['asset']['filename']}' CREATED :: mapping {assetUID} -> {res['asset']['uid']}")

        with open('./data/mapping/assets.json', 'w') as f:
            f.write(json.dumps(assetsMap, indent=4))

    utils.log('assets sync END', verbose=True)
