def remove_duplicates(dicts):
    unique_dicts = []
    seen_ids = set()
    for dictionary in dicts:
        if dictionary["id"] not in seen_ids:
            unique_dicts.append(dictionary)
            seen_ids.add(dictionary["id"])
    return unique_dicts
