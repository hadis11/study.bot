def merge_tuples(tuple_list):
    merged = {}
    
    for t in tuple_list:
        key = t[0]
        merged[key] = (t[1], t[2], t[3])

    return merged
