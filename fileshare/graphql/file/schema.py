import strawberry

@strawberry.type
class FileQuery:
    """A Query class for files"""

    all_files: List[]
