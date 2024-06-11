from scoring.helper import dlog


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


def get_user_dict(user_ids):
    user_id_dict = {}
    for i, u_id in enumerate(user_ids):
        user_id_dict.update({u_id: i})
    return user_id_dict


def get_header(user_ids, features):

    # BLOCK A
    header = ["ID", "Path", "Filename", "Useless", "Score-Count", ""]

    # BLOCK B
    for i, u_id in enumerate(user_ids):
        header.extend([f"{ft} Scorer {u_id}" for ft in features])
        header.extend([f"Σ Scorer {u_id}", f"Mean Scorer {u_id}", ""])

    # BLOCK C
    for u_id in user_ids:
        header.append(f"Comment Scorer {u_id}")

    # BLOCK D
    header.extend([""])
    header.extend([f"Variance {ft}" for ft in features])
    header.extend(["Variance (Σ)"])

    dlog("Header:", header)

    return header
