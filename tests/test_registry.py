from pathlib import Path
import urllib.request as request
from urllib.error import HTTPError
import yaml


def test_registry():
    """Test that all files in the registry are available at the expected URLs"""

    registry = Path(__file__).parent.parent / 'registry.yml'
    with open(registry, 'r') as f:
        registry = yaml.safe_load(f)

    # Get download url for each mapping set

    for i in registry['mapping_set_references']:
        if 'mirror_from' in i:
            url = i['mirror_from']
            try:
                r = request.urlopen(url)
            except HTTPError:
                raise Exception(f"{url} cannot be downloaded from mirror location")

if __name__ == '__main__':
    test_registry()
