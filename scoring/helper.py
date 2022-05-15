import os
import pathlib

from server.settings import MEDIA_ROOT


def save_check_dir(*dirs):
    for _d in dirs:
        if not os.path.isdir(_d):
            print(f"Created {_d}")
            pathlib.Path(_d).mkdir(parents=True, exist_ok=True)


def get_media_path() -> str:
    return "media"


def get_project_evaluation_dir(project_id) -> str:
    _path = build_abs_path(["evaluations", project_id])
    save_check_dir(_path)
    return _path


def build_abs_path(path_list: list) -> str:
    _abs_path = os.path.abspath(MEDIA_ROOT)
    return os.path.join(_abs_path, *path_list)


# Hardcopy from https://github.com/Shamya/FleissKappa
# Thank you!
'''
Created on Aug 1, 2016
@author: skarumbaiah

Computes Fleiss' Kappa 
Joseph L. Fleiss, Measuring Nominal Scale Agreement Among Many Raters, 1971.
'''


def checkInput(rate, n):
    """
    Check correctness of the input matrix
    @param rate - ratings matrix
    @return n - number of raters
    @throws AssertionError
    """
    N = len(rate)
    k = len(rate[0])
    print("RATE", rate, N, k)
    # print("RATE2", (len(rate[1]) == k for 1 in range(k))

    assert all(len(rate[i]) == k for i in range(k)), "Row length != #categories)"
    assert all(isinstance(rate[i][j], int) for i in range(N) for j in range(k)), "Element not integer"
    assert all(sum(row) == n for row in rate), "Sum of ratings != #raters)"


def fleissKappa(rate, n):
    """
    Computes the Kappa value
    @param rate - ratings matrix containing number of ratings for each subject per category
    [size - N X k where N = #subjects and k = #categories]
    @param n - number of raters
    @return fleiss' kappa
    """

    N = len(rate)
    k = len(rate[0])
    print("#raters = ", n, ", #subjects = ", N, ", #categories = ", k)
    # checkInput(rate, n)

    # mean of the extent to which raters agree for the ith subject
    PA = sum([(sum([i**2 for i in row]) - n) / (n * (n - 1)) for row in rate])/N
    print("PA = ", PA)

    # mean of squares of proportion of all assignments which were to jth category
    PE = sum([j**2 for j in [sum([rows[i] for rows in rate])/(N*n) for i in range(k)]])
    print("PE =", PE)

    kappa = -float("inf")
    try:
        kappa = (PA - PE) / (1 - PE)
        kappa = float("{:.3f}".format(kappa))
    except ZeroDivisionError:
        print("Expected agreement = 1")

    print("Fleiss' Kappa =", kappa)

    return kappa
