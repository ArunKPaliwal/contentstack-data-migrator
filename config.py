config = {
    'hostCD': 'https://eu-cdn.contentstack.com/v3',
    'hostCM': 'https://eu-api.contentstack.com/v3',
    'master_locale': {
        'name': 'English - United States',
        'code': 'en-us'
    },
    'source_stack': 'blte04ed78XXXXXXX',
    'destination_stack': 'blt2a50a29XXXXXXXXX',
    'source_management_token': 'cscd0dd361b96a9XXXXXXXXX',
    'destination_management_token': 'csaa289fc4975a7XXXXXXXX',
    'source_delivery_token': 'csb947b5571b33993XXXXXXX',
    'source_environment': 'prod',
    'destination_environment': 'production'
}

deliveryHeaders = {
    'api_key': config['source_stack'],
    'access_token': config['source_delivery_token']
}

sourceHeaders = {
    'api_key': config['source_stack'],
    'authorization': config['source_management_token']
}

destinationHeaders = {
    'api_key': config['destination_stack'],
    'authorization': config['destination_management_token']
}

assetParentUID = 'blt4be7337XXXXXXX'

list_only = False

from_date = '2021-06-20'
