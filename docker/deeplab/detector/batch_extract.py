import argparse
import os
import extract_MGS_frames as e


def process_folder(folder, model, num, lhth, rmframes):
    for root, _, files in os.walk(folder):
        for f in files:
            if '.' in f and f.rsplit('.', 1)[-1].lower() in ['avi', 'mp4']:
                vpath = os.path.join(root, f)
                # if not "SUB" in vpath: continue # for the case, where only video snippets created by ffmpeg should be considered
                print(f"\n====Processing video {vpath}====")
                path_a = f"{vpath.rsplit('.', 1)[0]}_MGSframes"
                path_b = f"{vpath.rsplit('.', 1)[0]}_infofile.txt"
                if os.path.exists(path_a) or os.path.exists(path_b):
                    print("Video has already been processed. Continuing.")
                    continue
                e.extract_frames(vpath, model, num, lhth, rmframes)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Extracts frames suitable for MGS analysis from all videos in a folder tree. See extract_MGS_frames.py for details.")
    p.add_argument('folder', help="The parent folder with videos in it or subdirectories.")
    p.add_argument("-m", "--model",
                   help="The config.yaml file of the trained DLC model. Default: It is assumed, that it has already been applied and the script looks for the results next to the video",
                   default=None)
    p.add_argument("-n", "--num_candidates",
                   help="The maximum number of face detections to return for each mouse. Will be less than this, if there were fewer frames. Experience shows, that when one chooses number bigger than 20 or so, that there will be quite a few suboptimal detections with nose cropped off etc. Default: 15",
                   default=15, type=int)
    p.add_argument("-l", "--likelihood_thresh", help="The threshold under which a detection is not used. Default: 0.8",
                   default=.8, type=float)
    p.add_argument('-kf', '--keep_frames',
                   help="If this is set, the folder with all of the frames in the video, that is created for this program, is kept and not deleted. This does not affect the output folder with the MGS-suitable images.",
                   action="store_true")
    args = p.parse_args()
    process_folder(args.folder, args.model, args.num_candidates, args.likelihood_thresh, not args.keep_frames)
