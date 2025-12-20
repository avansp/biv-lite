from biv_lite import BivFrames, BivParametric
import numpy as np
import copy
from scipy import stats
from loguru import logger
from biv_align.spike_detector import mad_lm


def impute_biv_frames(biv_in: BivFrames, smoothing: float = 0.0, verbose: bool = False) -> BivFrames:
    """Just perform imputation on missing frame.
    
    Note that this will not modify the biv input.
    """
    ts = np.arange(len(biv_in)) / len(biv_in)
    biv_out = copy.deepcopy(biv_in)

    empty_frames = np.argwhere([b.is_empty() for b in biv_out]).flatten()
    if len(empty_frames) == 0:
        return biv_out
    
    try:
        bp = BivParametric(biv_out, smoothing=smoothing)

        # replace biv_1 with imputation
        biv_out = bp(ts)

        if verbose:
            logger.info(f"Imputed {len(empty_frames)} frames.")

    except Exception as err:
        logger.error(f"Failed creating a BivParametric object - {err}")
        return None
    
    return biv_out
    

def clean_biv_frames(biv_in: BivFrames,
                     outlier_d: float = 1.5,
                     first_smoothing: float = 0.0,
                     second_smoothing: float = 50.0,
                     spike_threshold: float = 2.0,
                     verbose: bool = False) -> dict | None:
    """Perform imputation, outlier detection, and spike removals on the BivFrames.
    
    The output is a dictionary or None.
    """
    
    # first pass: find outliers and make them empty
    vol_in = np.array(biv_in.lv_endo_volumes())
    empty_frames = np.argwhere([b.is_empty() for b in biv_in]).flatten()
    if verbose:
        logger.info(f"Found {len(empty_frames)} empty frames at {empty_frames}.")

    # outlier is based on IQR: < Q1 - outlier_d * IQR or > Q3 + outlier_d * IQR
    up_bound = stats.quantile(vol_in, 0.75, nan_policy='omit') + outlier_d * stats.iqr(vol_in, nan_policy='omit')
    lo_bound = stats.quantile(vol_in, 0.25, nan_policy='omit') - outlier_d * stats.iqr(vol_in, nan_policy='omit')    
    outliers = np.argwhere(np.logical_or(vol_in > up_bound, vol_in < lo_bound)).flatten()
    
    # create a copy of biv_in into biv_out, then make the outliers as empty frames
    biv_out = copy.deepcopy(biv_in)
    biv_out.make_frames_empty(outliers)

    if verbose:
        logger.info(f"Found {len(outliers)} outliers at {outliers}; vols = {vol_in[outliers]}")

    # first imputation: missing frames + outliers
    biv_out = impute_biv_frames(biv_out, smoothing=first_smoothing, verbose=verbose)
    if biv_out is None:
        return None

    # second pass: find spikes and make them empty frames
    vol_out = np.array(biv_out.lv_endo_volumes())
    spikes = np.argwhere(mad_lm(vol_out) > spike_threshold).flatten()
    biv_out.make_frames_empty(spikes)

    if verbose:
        logger.info(f"Found {len(spikes)} spikes at {spikes}.")

    # second imputation: spike removed + missing frames if there wasn't outliers
    biv_out = impute_biv_frames(biv_out, smoothing=second_smoothing, verbose=verbose)
    if biv_out is None:
        return None
    
    return { 
        'biv': biv_out,
        'empty': empty_frames,
        'spikes': spikes,
        'outliers': outliers
    }

        
