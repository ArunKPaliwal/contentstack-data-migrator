import json
import os

import requests

import config


try:
    os.makedirs('./data/mapping')
except FileExistsError:
    pass

assetsMap = {}
assetsDirMap = {}

with open('./data/mapping/assets.json') as f:
    assetsMap = json.load(f)

with open('./data/mapping/assetsDir.json') as f:
    assetsDirMap = json.load(f)

def getAssets(assets, assetsDir, headers):
    flag = True
    skip = 100
    limit = 100
    cnt = 0
    while flag:
        res = requests.get(config.config['hostCM'] + '/assets?include_folders=true&include_count=true&skip=' + str(skip * cnt) + '&limit=' + str(limit), headers=headers).json()
        for asset in res['assets']:
            if asset['is_dir']:
                if (asset['uid'] in assetsDirMap.keys()) or (asset['uid'] in assetsDirMap.values()):
                    continue
                assetsDir[asset['name']] = asset['uid']
            else:
                if (asset['uid'] in assetsMap.keys()) or (asset['uid'] in assetsMap.values()):
                    continue
                assets[asset['content_type'] + asset['filename']] = asset['uid']
        cnt = cnt + 1
        if res['count'] <= skip * cnt:
            flag = False
    return assets, assetsDir


assetsSrc = {}
assetsDirSrc = {}
assetsSrc, assetsDirSrc = getAssets(assetsSrc, assetsDirSrc, config.sourceHeaders)

assetsDst = {}
assetsDirDst = {}
assetsDst, assetsDirDst = getAssets(assetsDst, assetsDirDst, config.destinationHeaders)

for asset in assetsDst:
    if asset in assetsSrc:
        assetsMap[assetsSrc[asset]] = assetsDst[asset]

for Dir in assetsDirDst:
    if Dir in assetsDirSrc:
        assetsDirMap[assetsDirSrc[Dir]] = assetsDirDst[Dir]

with open('./data/mapping/assets.json', 'w') as f:
    f.write(json.dumps(assetsMap, indent=4))

with open('./data/mapping/assetsDir.json', 'w') as f:
    f.write(json.dumps(assetsDirMap, indent=4))
