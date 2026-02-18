import numpy as np


def relative_madness(y: np.array, w: int = 3):
    """
    Compute relative MADness (MAD = median absolute deviation).

    The relative madness is defined as the absolute difference between a point and the median of its
    immediate neighbours, minus the median absolute deviation of the three points.
    This can be used to identify spikes in a signal.

    Source: https://gist.github.com/w121211/fbd35d1a8776402ac9fe24654ca8044f

    The definition of relative MADness for window w=3 for point at y(i) is given as follows:
        median_i = median([y(i-1), y(i), y(i+1)])
        mad(i) = | y(i) - median_i |

        rel_mad(i) = mad(i) - median([ | y(j) - median_i |, for {j in [i-1, i, i+1]} ])

    The implementation below has been optimized for all points of y

    Note that spike can be detected as relative madness > 2.

    Args:
        y (np.array): 1D array of values.
    Returns:
        np.array: 1D array of relative madness values.
    """
    # create a matrix of windows with width = w
    rolls = np.arange(int((w-1)/2), -int((w-1)/2)-1, -1)
    yx = np.column_stack(tuple(np.roll(y,r) for r in rolls))

    # compute median_i at each window
    med_w = np.median(yx, axis=1)

    # compute all relative MADness for all points i
    rm = np.abs(y - med_w) - np.median( np.abs(yx - np.tile(med_w, (w,1)).T), axis=1 )

    return rm


def mad_lm(y: np.array, w: int = 3):
    """
    Detect spikes from relative madness of the base linear model deviation.

    This is an improved version of relative madness, where the input to that spike detection is the y,
    but the relative deviation of each point to the linear model defined by its base points.

    Let [y1, y2, y3] are three points on y and we want to check whether y2 is a spike or not.

    First, define a linear model based on y1 and y3 as follows:
        L13 = 0.5 * (y3 - y1) + y1

    Then calculate the absolute deviation of y2 from L13:
        d2 = abs(y2 - L13)

    Using all values of y, the input for relative_madness becomes absolute deviations for all points.
    """
    # create matrix of 3 window
    yx = np.column_stack((np.roll(y, 1), y, np.roll(y, -1)))

    # apply linear equation between end points and calculate the difference in the middle point
    lm_devs = np.abs(yx[:,1] - (0.5 * (yx[:,2] - yx[:,0]) + yx[:,0]))

    # then return its relative madness
    return relative_madness(lm_devs, w=w)

