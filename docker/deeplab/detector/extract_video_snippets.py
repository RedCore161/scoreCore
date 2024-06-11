"""
    @author Niek Andresen
    @date Aug 2021
    Can extract a video snippet from a longer video given start and end times.
    Also offers a function to do that on a list of videos given in a table.
"""

import os
import pandas as pd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def time_str_to_secs(time):
    return sum(x * float(t) for x, t in zip([1, 60, 3600], reversed(time.split(":"))))


def extract_snippet(vid_path, start, end, out_folder=None):
    """
        expects start and end to be times like "00:15:07.15" for a bit more than 15 minutes. "15:07.15" is also ok.
        With out_folder None the snippet will be put next to the video
    """
    if isinstance(start, str):
        rm12h_start = "AM" in start
        rm12h_end = "AM" in end
        start = start.strip("' AMP")
        end = end.strip("' AMP")
        try:
            start = time_str_to_secs(start)
            end = time_str_to_secs(end)
        except ValueError:
            print(f"ERROR: could not convert {start} or {end} to float for video {vid_path}.")
            raise
        if rm12h_start: start -= 12 * 3600
        if rm12h_end: end -= 12 * 3600
    else:
        print(
            f"ERROR: times have to be given as strings, everything else not yet implemented. Times given: {start}, {end}")
        exit(1)
    if out_folder is None:
        out_path = None
    else:
        out_path = os.path.join(out_folder, os.path.basename(vid_path))
        out_path, suffix = out_path.rsplit('.', 1)
        out_path = out_path + f"SUB{int(start * 1e3)}_{int(end * 1e3)}" + '..' + suffix
    ffmpeg_extract_subclip(vid_path, start, end, targetname=out_path)


def extract_snippets_listed(table_file, folder, out_folder=None):
    table = pd.read_excel(table_file, engine="openpyxl")
    errors = []
    prints_file = os.path.join(os.path.dirname(table_file), 'extract_snippets_prints.txt')
    with open(prints_file, 'w') as printsf:
        for idx, row in table.iterrows():
            if pd.isnull(row["folder"]): break
            fpath = os.path.join(folder, row['filename'] + '.mp4')
            if os.path.exists(fpath):
                try:
                    extract_snippet(fpath, str(row['start']), str(row['end']), out_folder)
                except Exception as e:
                    print(str(e))
                    errors.append((fpath, row, str(e)))
                    continue
            else:
                print(fpath)
                s = f"ERROR: Video file {fpath} does not exist. This is the table entry: {row}\nSkipping."
                print(s)
                printsf.write(s)
        print("Done.")
        printsf.write("Done.")
        if len(errors) > 0:
            print("Errors:")
            printsf.write("Errors:\n")
            for e in errors:
                print("===", e[0], ":")
                print(e[1])
                print(e[2])
                printsf.write(f"=== {e[0]} :\n{e[1]}\n{e[2]}")


def extract_snippets_listed_frontside(table_file, folder, out_folder=None):
    # find all video files
    vids = dict()
    for d, _, files in os.walk(folder):
        for f in files:
            if f.endswith('.avi') or f.endswith('.mp4'):
                vids[f] = d
    # extract video snippets
    tables = pd.read_excel(table_file, engine="openpyxl", sheet_name=None)
    errors = []
    prints_file = os.path.join(os.path.dirname(table_file), 'extract_snippets_prints.txt')
    with open(prints_file, 'w') as printsf:
        printsf.write(f"extract_video_snippets.py\nFolder with videos: {folder}\nExcel table: {table_file}\n\n")
        for sheet in tables.keys():
            if "Batch" not in sheet: continue
            printsf.write(f"-Sheet: {sheet}\n")
            for persp in ['Front', 'Side']:
                printsf.write(f"--Perspective: {persp}\n")
                fname_col = f"Clip - {persp}"
                start_col = f"{persp} Timestamp - Start"
                end_col = f"{persp} Timestamp - END"
                for idx, row in tables[sheet].iterrows():
                    if pd.isnull(row[fname_col]): continue
                    if row[fname_col] + '.mp4' in vids.keys():  # if os.path.exists(fpath):
                        fpath = os.path.join(vids[row[fname_col] + '.mp4'], row[fname_col] + '.mp4')
                        try:
                            extract_snippet(fpath, str(row[start_col]), str(row[end_col]), out_folder)
                        except Exception as e:
                            print(str(e))
                            errors.append((fpath, row, str(e)))
                            continue
                    else:
                        print(fpath)
                        s = f"ERROR: Video file {fpath} ({persp}) does not exist. This is the table entry:\n{row}\nSkipping.\n"
                        print(s)
                        printsf.write(s)
                print("Done.")
                printsf.write("Done.\n")
                if len(errors) > 0:
                    print("Errors:")
                    printsf.write("Errors:\n")
                    for e in errors:
                        print("===", e[0], ":")
                        print(e[1])
                        print(e[2])
                        printsf.write(f"=== {e[0]} :\n{e[1]}\n{e[2]}")


tab = "/home/niek/tubCloud/Shared/scioi_proj-003/black_mice_paper_2/Tables_regarding_datasets/BLang/TestList.xlsx"  # "/home/niek/Data/MGS_faces_JWitz/MGS-Videos_osmotische_Pumpe_Wilzopolski1_20210719.xlsx"
extract_snippets_listed_frontside(tab, "/home/niek/tmp/BLang",
                                  "/home/niek/tmp/BLang/output")  # "/media/niek/My Book/FU-Veterinärpharmakologie_Jenny_Wilzopolski_G0204_20")
