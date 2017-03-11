"""Simple module to download files from a remote location."""


import urllib.request


def download_from_to(from_location, to_file_path):
    """Simple access wrapper to download from a remote location."""
    # urllib.request.urlretrieve('http://example.com/big.zip', 'file/on/disk.zip')
    urllib.request.urlretrieve(from_location, to_file_path)
