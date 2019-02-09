from ayrabo.utils import chunk


def get_chunked_divisions(divisions, per_row=4):
    # The generator gets exhausted after the first iteration over the items. Convert to a list here to prevent this
    # problem.
    return list(chunk(divisions, per_row))
