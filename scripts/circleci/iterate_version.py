import os, sys

MAJOR=0
MINOR=1
MICRO=2

script_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(os.path.dirname(script_dir))
version_file = os.path.join(project_dir, 'src', 'scrilla' 'version.txt')

def load_current_version():
    with open(version_file, 'r') as f:
        version = f.read()
    return version

def save_new_version(version_str):
    with open(version_file, 'w') as f:
        f.write(version_str)

def to_version_array(version_string):
    version_array = version_string.split('.')
    return [ int(x) for x in version_array ]

def to_version_string(version_array):
    version_string_array = [ str(x) for x in version_array ]
    return '.'.join(version_string_array)

def iterate_index(version_string, version_index):
    version_array = to_version_array(version_string)
    version_array[version_index] += 1
    return to_version_string(version_array)

def reset_index(version_string, version_index):
    version_array = to_version_array(version_string)
    version_array[version_index] = 0
    return to_version_string(version)

if __name__=="__main__":
    version = load_current_version()
    parsed_args = [ str(x).lower() for x in sys.argv]
    if 'major' in parsed_args:
        version = iterate_index(version, MAJOR)
        version = reset_index(version, MINOR)
        version = reset_index(version, MICRO)
    if 'minor' in parsed_args:
        version = iterate_index(version, MINOR)
        version = reset_index(version, MICRO)
    if 'micro' in parsed_args:
        version = iterate_index(version, MICRO)
    save_new_version(version)