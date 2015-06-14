import os, glob
from kodipopcorntime.common import RESOURCES_PATH

def get_providers():
    providers = {'movies':[],'meta':[],'subtitle':[]}
    for f in glob.glob(os.path.join(RESOURCES_PATH, 'lib', 'kodipopcorntime', 'providers', 'movie.*')):
        s = os.path.basename(f).split('_')
        if not len(s) == 2 or s[0] not in ['movies', 'meta', 'subtitle']:
            continue
        fModule = '{st}.{nd}'.format(st=s[0], nd=s[1].split('.')[0])
        providers[s[0]].append('kodipopcorntime.providers.'+fModule)
        providers.update({
            fModule: 'kodipopcorntime.providers.'+fModule
        })
    return providers

PROVIDERS = get_providers()