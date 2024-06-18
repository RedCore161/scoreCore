from scoring.helper import dlog, find_object_by_id


def get_cell(value) -> str:

    if value < 65:
        raise Exception("Unexpected value", value)
    if value <= 90:
        return chr(value)

    init = 64  # pre char 'A'

    while value > 90:
        value -= 26
        init += 1

    if init == 64:
        return chr(value)
    else:
        return f"{chr(init)}{chr(value)}"


def get_user_dict(user_ids, users=None):
    user_id_dict = {}
    for i, u_id in enumerate(user_ids):
        user_id_dict.update({u_id: {"pos": i, "name": find_object_by_id(users, u_id).get("username")}})
    return user_id_dict


def get_header(user_ids, features):

    # BLOCK A
    header = [{"name": "ID", "bck": 1, "cell": "A"},
              {"name": "Path", "bck": 1, "cell": "B"},
              {"name": "Filename", "bck": 1, "cell": "C"},
              {"name": "Useless", "bck": 1, "cell": "D"},
              {"name": "Score-Count", "bck": 1, "cell": "E"},
              {"name": "", "bck": 1, "cell": "F", "end": True}]

    # BLOCK B
    for i, u_id in enumerate(user_ids):
        header.extend([{"name": f"{ft} Scorer {u_id}", "bck": 2} for ft in features])
        header.extend([{"name": f"Σ Scorer {u_id}", "bck": 2},
                       {"name": f"Mean Scorer {u_id}", "bck": 2},
                       {"name": "", "bck": 2, "end": True}])

    # BLOCK C
    for u_id in user_ids:
        header.append({"name": f"Comment Scorer {u_id}", "bck": 3})

    # BLOCK D
    header.extend([{"name": "", "bck": 4}])
    header.extend([{"name": f"Variance {ft}", "bck": 4} for ft in features])
    header.extend([{"name": "Variance (Σ)", "bck": 4, "end": True}])

    dlog("Header:", header)

    return header
