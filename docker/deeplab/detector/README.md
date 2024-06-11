To go from mouse videos to MGS rateable image files. Use the script extract_MGS_frames.py

Steps that are performed:
 * Run the facial feature detector (use DLC api)
 * Use heuristic to extract frames
  * Not blurry (how to know?)
  * Frames not too close in time (not too similar)
  * As many facial features visible as possible

For videos, that show two mice in adjacent cages, use code in "mgs_frames_leftright" with
a DLC multianimal project.

Old code used for black mice v2 faces can be found in "detectors_blackmice_v2". It relies
on an adjusted version of an old version of DLC, so it is not recommended. It is replaced
by the code here.
