def get_version():
    with open('version.txt', 'r') as file:
        version = file.read().strip()
    return version

app_version = str(get_version())