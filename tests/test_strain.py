from biv_lite import BivFrames
import numpy as np
import pandas as pd


def test_gls(sample_biv: BivFrames, sample_gls: dict):
    gls = sample_biv.gls(ed_frame=0)

    for k in ['LV_GLS_2CH', 'LV_GLS_4CH', 'RVS_GLS_4CH', 'RVFW_GLS_4CH']:
        assert np.allclose(gls[k], sample_gls[k], rtol=0, atol=1e-4)    


def test_gcs(sample_biv: BivFrames, sample_gcs: dict):
    gcs = sample_biv.gcs(ed_frame=0)

    for k in ['LV_GCS_APEX', 'LV_GCS_MID', 'LV_GCS_BASE',
              'RVS_GCS_APEX', 'RVS_GCS_MID', 'RVS_GCS_BASE',
              'RVFW_GCS_APEX', 'RVFW_GCS_MID', 'RVFW_GCS_BASE']:
        assert np.allclose(gcs[k], sample_gcs[k], rtol=0, atol=1e-3)    
