"""
    @author Niek Andresen
    @date March 2021
    
    This applies a trained DLC model to a new video.
"""

import deeplabcut as dlc
import argparse
import os


def find_pickle(vid):
    picklefile = None
    _dirname = os.path.dirname(vid)
    for f in os.listdir(_dirname):
        if "_bx.pickle" in f and os.path.basename(vid).rsplit(".", 1)[0] in f:
            if picklefile is not None:
                print(f"Error: Found several matching .pickle files in {_dirname}. Exiting.")
                exit(1)
            picklefile = os.path.join(_dirname, f)
    return picklefile


def find_detections(vid):
    """
    returns path to resulting file. If nothing was detected, because there were no mice in the video or the video
    file was corrupted, the resulting file does not exist.
    """
    det = None
    _dirname = os.path.dirname(vid)
    for f in os.listdir(_dirname):
        if ".h5" in f and os.path.basename(vid).rsplit('.', 1)[0] in f:
            if det is not None:
                print(f"Error: Found several matching .h5 files in {_dirname}. Exiting.")
                exit(1)
            det = os.path.join(_dirname, f)
    return det


def apply_dlc(vid, config_path):
    dlc.analyze_videos(config_path, [vid], save_as_csv=True)
    result_file = find_detections(vid)
    return result_file


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Applies an already trained DLC model to a video. "
                                                    "Resulting .h5 file will be put next to the video.")
    argparser.add_argument("video", help="Video file on which to apply the model.")
    argparser.add_argument("config", help="Path to the config.yaml file of the trained DLC model.")
    a = argparser.parse_args()
    res = apply_dlc(a.video, a.config)
    print("Result:", res)
