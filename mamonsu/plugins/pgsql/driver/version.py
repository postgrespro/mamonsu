import re

def extract_version(raw_version):
    match = re.search(r'\d+(?:\.\d+)*', raw_version)

    if match:
        return match.group(0)

    return ''