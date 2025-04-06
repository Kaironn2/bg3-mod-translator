MAJOR = 36028797018963968
MINOR = 140737488355328
REVISION = 2147483648

def calculate_version64(major: int, minor: int, revision: int, build: int) -> int:
    major = major * MAJOR
    minor = minor * MINOR
    revision = revision * REVISION
    return major + minor + revision + build