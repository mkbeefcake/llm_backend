def remove_duplicates(dicts, by: str = "id"):
    unique_dicts = []
    seen_ids = set()
    for dictionary in dicts:
        if dictionary[by] not in seen_ids:
            unique_dicts.append(dictionary)
            seen_ids.add(dictionary[by])
    return unique_dicts
