"""
    @author Niek Andresen
    @date Mar 2021
    
    Takes a video and extracts some frames from it, that are well suited for MGS
    judgment. Looks at blur and the visibility of mouse facial features.
    
    Steps:
    - Detect facial features with a trained DLC model
    - Find suitable frames by balancing the number of detected features and the likelihoods of the detections
    - Determine the face bounding boxes
    - Extract the requested frames from the video file
    - Crop the faces and save the cropped images
    - Rank the results by blurriness and store the order in a 'infofile.txt' file next to the crops

    The application of the trained model to find the facial features requires GPU (e.g. with the DLC docker).
    The rest is done on CPU. All frames of the video are extracted at one point requiring at least 12GB free.
    The whole script takes about an hour for one of the three minute videos of the dataset on the GTX 1060
    and about half that time one the Quadro RTX 4000.
"""

import cv2
import os
from shutil import rmtree
import argparse
from video_to_frames import video_to_frames as get_frames
from detect_blur import detect_blur_fft
import face_detector.detections_to_face as fd
from crop_faces import crop
import numpy as np



# def plot_rec(img, bbox):
#    plt.imshow(img)
#    ax = plt.gca()
#    h, w = bbox[1] - bbox[0], bbox[3] - bbox[2]
#    rect = Rectangle((bbox[2], bbox[0]), width=w, height=h, linewidth=1, edgecolor='r', facecolor='none')
#    ax.add_patch(rect)


def show_img(img, win_name="image"):
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1280, 640)  # 960, 540)
    cv2.imshow(win_name, img)
    cv2.waitKey(0)


def get_video_shape(vid):
    vcap = cv2.VideoCapture(vid)
    if vcap.isOpened():
        width = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return (int(width), int(height))


def get_ranks(arr):
    temp = np.array(arr).argsort()[::-1]
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(arr))
    return ranks


def extract_frames(vpath, model, num, lhth, rmframes=False):
    dirname_vpath = os.path.dirname(vpath)
    name = vpath.rsplit('.', 1)[0]

    # call DLC to detect facial features in the video - takes about 40 minutes on GTX 1060, 20 minutes on Quadro RTX 4000 (if model was given, otherwise it is assumed it has been applied before and the results are searched)
    if model is None:  # if no DLC model was given, it could be, that the DLC results are already there. That is checked here.
        dlc_feats = None
        for f in os.listdir(dirname_vpath):
            if f.endswith('_bx.h5') and os.path.basename(vpath).rsplit('.', 1)[0] in f:
                if dlc_feats is not None:
                    print(f"Error: Found several matching files in {os.path.dirname(dirname_vpath)}, "
                          f"that could be the detected features of the given video. Exiting.")
                    exit(1)
                dlc_feats = os.path.join(dirname_vpath, f)

        if dlc_feats is None:
            print(f"Error: Found no detected features in {dirname_vpath}."
                  f"Give -m <pathToTrainedModelConfig> and try again. Exiting.")
            exit(1)

        corr_path = dlc_feats.replace("bx.h5", "bx_lrcorrected.csv")
        if os.path.exists(corr_path):
            dlc_feats = corr_path

    else:  # A DLC model was given. Use it to detect the facial features (better use GPU computer).
        import call_DLC as applyDLC
        print("Applying DeepLabCut.")
        dlc_feats = applyDLC.apply_dlc(vpath, model)

    if dlc_feats is None or not os.path.exists(dlc_feats):  # nothing was detected or the video file is corrupted
        with open(name + "_infofile.txt", 'w') as f:
            f.write(f"No faces for MGS rating could be extracted from video {vpath}. "
                    f"Check the video, maybe it doesn't show mice or it is corrupted.\n")
        return

    # get face detections from DLC detections (takes about 7 minutes (num=1000))
    print("Computing Face Bounding Boxes.")
    shape = get_video_shape(vpath)
    faces = fd.main(dlc_feats, num, lhth, shape)
    frame_indices = faces[0]

    # extract frames, if it hasn't been done yet (takes less than 10 minutes)
    print("Extracting frames from the video.")
    frames_folder = name + "_frames"
    if not os.path.exists(frames_folder):
        get_frames(vpath, frames_folder, frames_to_extract=frame_indices)
    else:
        print(f"Warning: Frames folder exists. This means no new frames are extracted, which could cause an error "
              f"if other frames are needed.\nIn case of that error, delete the frames folder {frames_folder} and try again.")

    # plot for looking at results
    # for m, d in faces.items():
    #    for idx, face in zip(d[0], d[1]):
    #        img = imread(os.path.join(frames_folder, f"{idx:05d}.png"))#cv2.imread(os.path.join(frames_folder, f"{idx:05d}.png"), cv2.IMREAD_GRAYSCALE)
    #        plot_rec(img, face)
    #        plt.show()

    print("Cropping faces out, computing blur and writing logfile.")

    # crop faces out
    result_folder = name + "_MGSframes"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        for idx, bbox in zip(faces[0], faces[1]):
            fname = f"{idx:05d}.png"
            crop(os.path.join(frames_folder, fname), bbox, os.path.join(result_folder, fname))

    #TODO
    # if rmframes:
    #     rmtree(frames_folder)

    # blur detection
    # Uses two methods. Ranks the results by their performance in each method and then orders them by their average rank.
    laps = []
    fftbs = []
    for idx, face in zip(faces[0], faces[1]):
        img = cv2.imread(os.path.join(result_folder, f"{idx:05d}.png"), cv2.IMREAD_GRAYSCALE)
        laps.append(cv2.Laplacian(img, cv2.CV_64F).var())
        fftbs.append(detect_blur_fft(img)[0])
        # show_img(img, f"Lap {laps[-1]}, FFT {fftbs[-1]}")
    sorted_by_avg_rank = np.argsort([(v[0] + v[1]) / 2 for v in zip(get_ranks(laps), get_ranks(fftbs))])
    faces = ([faces[0][i] for i in sorted_by_avg_rank], [faces[1][i] for i in sorted_by_avg_rank])

    # plot for looking at results
    # for m, d in faces.items():
    #    mresfolder = os.path.join(result_folder, m)
    #    rank = 0
    #    for idx in d[0]:
    #        img = imread(os.path.join(mresfolder, f"{idx:05d}.png"))
    #        plt.imshow(img)
    #        plt.title(f"{m} frame {idx} blur rank {rank} (0 is best)")
    #        plt.show()
    #        rank += 1

    # write blurriness ranking/log file
    with open(os.path.join(result_folder, 'infofile.txt'), 'w') as f:
        f.write(f"Frames for MGS rating\nextracted from video {vpath}.\nSorted by blurriness (best quality to worst):\n")
        for idx in faces[0]:
            f.write(f"{idx:05d}.png\n")
        f.write("\nParams used:\n")
        f.write(f"video: {vpath}\ntrained model: {model}\nnumber of faces requested: {num}\n"
                f"likelihood threshold: {lhth}\nremove frames afterwards: {rmframes}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Extracts frames suitable for MGS analysis from a video. "
                                            "For this a trained DLC model is applied to find the facial features, "
                                            "then face bounding boxes are found.")
    p.add_argument('vid', help="The video with the mouse or mice.")
    p.add_argument("-m", "--model", help="The config.yaml file of the trained DLC model. Default: It is assumed, "
                                         "that it has already been applied and the script looks for the results next "
                                         "to the video", default=None)
    p.add_argument("-n", "--num_candidates", help="The maximum number of face detections to return for each mouse. "
                                                  "Will be less than this, if there were fewer frames. Experience shows,"
                                                  " that when one chooses number bigger than 20 or so, that there will be"
                                                  " quite a few suboptimal detections with nose cropped off etc. "
                                                  "Default: 15", default=15, type=int)
    p.add_argument("-l", "--likelihood_thresh", help="The threshold under which a detection is not used. Default: 0.8",
                   default=.8, type=float)
    p.add_argument('-kf', '--keep_frames', help="If this is set, the folder with all of the frames in the video, that is"
                                                " created for this program, is kept and not deleted. This does not affect"
                                                " the output folder with the MGS-suitable images.", action="store_true")
    args = p.parse_args()
    extract_frames(args.vid, args.model, args.num_candidates, args.likelihood_thresh, not args.keep_frames)
