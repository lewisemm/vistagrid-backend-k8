def owner_id_header_is_valid(owner_id):
    """
    Returns True if owner_id value is valid and returns False if otherwise.
    """
    if owner_id == None:
        return False
    for digit in owner_id:
        try:
            int(digit)
        except ValueError:
            return False
    return True
