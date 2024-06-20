import io
import os
import datetime
from collections import Counter

import pandas as pd

from scoring.helper import dlog, find_object_by_id, get_project_evaluation_dir, save_check_dir
from scoring.helper import elog, get_backend_url
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


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
              {"name": "URL", "bck": 1, "cell": "B"},
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
    header.extend([{"name": f"Std-Dev {ft}", "bck": 4} for ft in features])
    header.extend([{"name": "Std-Dev (Σ)", "bck": 4, "end": True}])

    dlog("Header:", header)

    return header


def create_xlsx(project, _data, _image_files):

    _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")
    _path = get_project_evaluation_dir(str(project.pk))
    save_check_dir(_path)

    _user_ids = project.get_all_scores_save().distinct("user").values_list("user__id", flat=True)

    df = pd.DataFrame()
    project_name = str(project.name)
    target = os.path.join(_path, f"{_file_template}.xlsx")

    features = project.get_features_flat()
    header = get_header(_user_ids, features)
    user_id_dict = get_user_dict(_user_ids, _data.get("project").get("users"))

    with pd.ExcelWriter(target, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=project_name)

        ws = writer.sheets[project_name]
        workbook = writer.book
        format_OK = workbook.add_format({"bg_color": "#00a077"})
        format_GRAY = workbook.add_format({"bg_color": "#bababa", "align": "center"})
        header_format = workbook.add_format({"text_wrap": True, "rotation": 90, "bold": True})
        ws.set_row(0, 150, header_format)

        # BLOCK widths
        block_counter = Counter(head["bck"] for head in header)
        BL_A = block_counter.get(1)
        BL_B = block_counter.get(2)
        BL_BL = len(features) + 2
        BL_C = block_counter.get(3)
        BL_D = block_counter.get(4)

        # Write Header
        for pos, head in enumerate(header):
            ws.write(0, pos, head.get("name"), header_format)
            if pos == 0 or pos > 3:
                ws.set_column(pos, pos, 3)

        line = 1
        for image_file in _image_files:
            queryset = image_file.get_scores_save(project).order_by("user__pk")
            stddevs = image_file.data

            if len(queryset) == 0:
                continue

            # BLOCK A
            ws.write(line, 0, line)
            ws.write_url(line, 1, os.path.join(get_backend_url(), image_file.path, image_file.filename), string="Link")
            ws.write(line, 2, image_file.filename)
            ws.write(line, 3, image_file.useless)
            ws.write(line, 4, image_file.scores.count())
            ws.write(line, 5, "")

            # BLOCK B - Write Data
            for score in queryset:
                data = score.data

                u_id = user_id_dict.get(score.user_id)
                if not u_id:
                    elog("Unused Score:", score)
                    continue

                pos = u_id.get("pos")
                for j, ft in enumerate(features):
                    _pos = BL_A + j + (pos * (BL_BL + 1))
                    ws.write(line, _pos, data.get(ft), format_GRAY if data.get(ft) == "X" else None)

                ABS_BL_B = BL_A + len(features)

                start_col = get_cell(65 + BL_A + (pos * (BL_BL + 1)))
                end_col = get_cell(64 + ABS_BL_B + (pos * (BL_BL + 1)))
                ws.write_formula(line, ABS_BL_B + (pos * (BL_BL + 1)), f"=SUM({start_col}{line + 1}:{end_col}{line + 1})")
                ws.write_formula(line, ABS_BL_B + (pos * (BL_BL + 1) + 1), f"=AVERAGE({start_col}{line + 1}:{end_col}{line + 1})")

            # BLOCK C - Write user-comments
            pos = BL_A + BL_B
            for score in queryset:
                u_id = user_id_dict.get(score.user_id)
                if not u_id:
                    continue
                ws.write(line, pos + u_id.get("pos"), score.comment)

            pos += 1 + BL_C

            # BLOCK D - Write stddev
            _sum = 0
            for j, ft in enumerate(features):
                _stddev = stddevs.get(f"stddev_{ft}")
                if _stddev:
                    _sum += _stddev
                ws.write(line, pos + j, _stddev)

            pos_var = BL_A + BL_B + BL_C + BL_D - 1
            ws.write(line, pos_var, _sum, format_OK if _sum == 0 else None)
            line += 1

        # List users
        line += 2
        for u_id, _dict in user_id_dict.items():
            ws.write(line, 1, f"Scorer {u_id}")
            ws.write(line, 2, _dict.get("name"))
            line += 1

        # List useless images
        line += 2
        for image_file in project.get_all_useless_files():
            ws.write(line, 0, line)
            ws.write(line, 1, image_file.path)
            ws.write(line, 2, image_file.filename)
            ws.write(line, 3, image_file.useless)
            line += 1

    return target


def data_to_image(data, title, max_score, x_axis, y_axis, x_label="Users", y_label="Users", figsize=(10, 8)):

    # Create a colormap that transitions from green to red
    cmap = LinearSegmentedColormap.from_list("green_red", ["green", "yellow", "red"])

    # Plot the heatmap
    plt.switch_backend("Agg")
    plt.figure(figsize=figsize)
    plt.imshow(data, cmap=cmap, aspect="auto", vmax=max_score)
    plt.colorbar()

    # Annotate the heatmap with the values
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            plt.text(j, i, f"{data[i, j]:.1f}", ha="center", va="center", color="black")

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(range(data.shape[1]), x_axis)
    plt.yticks(range(data.shape[0]), y_axis)

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    return buf
