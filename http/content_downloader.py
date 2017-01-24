import urllib.request


def download_from_to(from_location, to_file_path):
    # urllib.request.urlretrieve('http://example.com/big.zip', 'file/on/disk.zip')
    urllib.request.urlretrieve(from_location, to_file_path)
