import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime

import config
import utils
from assets import *
from content_types import *
from entries import *
from initial_sync import initial_sync


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument('service', type=str, default='all', help='service: [all/asset/assets/entry/entries/content_type/content_types]')
    parser.add_argument('-u', '--user', type=str, required=True, help='Username for logging')
    parser.add_argument('-d', '--from_date', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='date: [YYYY-MM-DD]')
    parser.add_argument('-l', '--list-only', help='list the updates only', action='store_true')
    parser.add_argument('--uid', help='uid of asset/content_type/entry to be updated/created', action='append')
    parser.add_argument('--ct', help='uid of content_type corresponding to entry', action='append')
    return parser.parse_args(sys.argv[1:])


args = parse_args()

config.from_date = args.from_date
config.list_only = args.list_only
print('\n')
utils.startLog()


def runAll():
    initial_sync()
    assets()
    content_types()
    entries()


utils.log(f'user: {args.user}', verbose=True)
if args.service == 'all':
    runAll()
elif args.service == 'asset':
    asset(args.uid)
elif args.service == 'assets':
    initial_sync()
    assets()
elif args.service == 'content_type':
    content_type(args.uid)
elif args.service == 'content_types':
    initial_sync()
    content_types()
elif args.service == 'entry':
    entry(args.uid, args.ct)
elif args.service == 'entries':
    initial_sync()
    entries()
else:
    print('Invalid argument: %s\nservice: [all/assets/entries/content_types]' % args.service)

utils.deleteBufferFiles()
print('Execution complete')
utils.endLog()
