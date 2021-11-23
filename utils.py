import shutil
from datetime import datetime


# utility function for topological sort
def topoSortUtil(key, visited, refs, ans):
    visited.add(key)
    for k in refs[key]:
        if k not in visited:
            topoSortUtil(k, visited, refs, ans)
    ans.append(key)


"""
    function to find topological sort
    input : graph is provided.
    ouput : a topo-sorted list.
"""
def topoSort(refs):
    ans = []
    visited = set()
    for key in refs:
        if key not in visited:
            topoSortUtil(key, visited, refs, ans)

    return ans


# Custom logger function to add logs into logs.log file
def log(args, verbose=False):
    if verbose:
        print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]", args)
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]", args, file=open('logs.log', 'a'))


def startLog():
    print('******Log Start******', file=open('logs.log', 'a'))


def endLog():
    print('******Log End******\n', file=open('logs.log', 'a'))


# Function to delete all the buffer files created during execution of process. Note: mappings are not deleted.
def deleteBufferFiles():
    try:
        shutil.rmtree('./data/assets')
    except Exception:
        pass
    try:
        shutil.rmtree('./data/content_types')
    except Exception:
        pass
    try:
        shutil.rmtree('./data/entries')
    except Exception:
        pass
    try:
        shutil.rmtree('./data/published')
    except Exception:
        pass


"""
    function to print changes that are to be made
    list : list of changes
    name : content_types/entries
    action : update/create
"""
def listChanges(list, name, action):
    if len(list) > 0:
        print(f'--The following {name} will be {action} in the destination stack:')
        for ind, item in enumerate(list):
            print(f"     {ind}. '{item}'")
        print()
        return True
    else:
        print(f'--No {name} to be {action} in the destination stack\n')
        return False


def confirmChanges():
    confirm = input('---Continue with the changes[yes/no]: ')
    while True:
        if confirm == 'no':
            print('---Aborting...')
            endLog()
            exit(1)
        elif confirm == 'yes':
            break
        else:
            print('---Invalid response')
            confirm = input('--Continue with the changes[yes/no]: ')
