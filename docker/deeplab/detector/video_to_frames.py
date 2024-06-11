"""
    @author Niek Andresen
    @date Feb 2020
    
    This gives the frames of a video as .png.
    It does no deinterlacing, so the frames have weird lines on the edges of moving objects.
    To use deinterlacing one can use:
    ffmpeg -i Superenrichment_Gruppe1_2.mts -vf yadif -q:v 2 -r 25 Superenrichment_Gruppe1_2_frames_ffmpeg/%04d.jpg -hide_banner
    (-vf yadif is the deinterlacing; -r 25 is the frame rate, which can be acquired by running this python script and then
    dividing the number of resulting frames by the duration of the video; -q:v 2 reduces the quality, but takes a lot less space,
    for lossless, omit -q:v 2 and use .png)
"""

import argparse
import cv2
import time
import os


def video_to_frames(input_loc, output_loc, frames_to_extract=None):
    """
    Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        input_loc: Input video file.
        output_loc: Output directory to save the frames.
        frames_to_extract: list of integers, that are frame indices (starting at 0 for the first frame) of those frames, that are supposed to be extacted. Default: None for all frames.
    Returns:
        None
    """
    if not os.path.exists(output_loc): os.makedirs(output_loc)
    # Log the time
    time_start = time.time()
    num_requested_frames = len(frames_to_extract) if frames_to_extract is not None else None
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    approx_video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    count = 0
    print("Converting video")
    # Start converting the video
    success, frame = cap.read()
    report_freq = 1e3
    print("\tReporting every {} frames:".format(report_freq))
    while success:  # cap.isOpened():
        if (count) % report_freq == 0: print(
            "\tFrame {} out of approximately {}..".format(count + 1, approx_video_length))
        # Write the results back to output location.
        if frames_to_extract is None or count in frames_to_extract:
            cv2.imwrite(os.path.join(output_loc, "{:05d}.png".format(count)),
                        frame)  # could add something like [cv2.IMWRITE_PNG_COMPRESSION, 0] or use .jpg to get it even smaller
            # frames_to_extract.remove(count) # a test revealed, that this slowed down the program a little (instead of the expected speed up)
        # Extract a frame
        success, frame = cap.read()
        count += 1
    # Release the feed
    cap.release()
    # Print stats
    num_for_message = count if num_requested_frames is None else num_requested_frames
    print("Done extracting frames. {} frames extracted.".format(num_for_message),
          "It took {:.2f} seconds.".format(time.time() - time_start))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Store the frames of a video as png.")
    argparser.add_argument("video_path", help="Path to the video file (.mp4, .mts, .avi)")
    argparser.add_argument('-o', "--output_dir",
                           help="Directory where the output should go. Will be created if it doesn't exist. Default: in a folder next to the video")
    argparser.add_argument('-f', "--frames",
                           help="List of frames (indices starting at 0) to extract. Default: all frames", nargs='+',
                           default=None)
    a = argparser.parse_args()
    if not a.output_dir:
        output_dir = a.video_path.rsplit('.', 1)[0] + "_frames"
    else:
        output_dir = a.output_dir
    if a.frames:
        a.frames = list(map(int, a.frames))
    video_to_frames(a.video_path, output_dir, a.frames)
