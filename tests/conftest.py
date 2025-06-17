import pytest
from pathlib import Path
import pandas as pd
import numpy as np
from biv_lite import BivFrames


@pytest.fixture(scope="function")
def sample_volumes() -> dict:
    """Read the sample frame volumes for comparison use"""
    vol_file = Path("tests") / "sample_frames" / "lvrv_volumes.csv"
    df = pd.read_csv(vol_file)
    df = df[df['name'] == "sample_frames"].sort_values(by='frame')

    assert np.array_equal(df['frame'].to_numpy(), np.arange(df.shape[0]))

    return {
        'lv_vol': df['lv_vol'].to_numpy(),
        'lvm': df['lvm'].to_numpy(),
        'rv_vol': df['rv_vol'].to_numpy(),
        'rvm':df['rvm'].to_numpy(),
        'lv_epivol': df['lv_epivol'].to_numpy(),
        'rv_epivol': df['rv_epivol'].to_numpy()
    }


@pytest.fixture(scope="function")
def sample_biv() -> BivFrames:
    """Load the sample models as BivFrames"""
    return BivFrames.from_folder(Path("tests") / "sample_frames", pattern="*_Model_Frame_*.txt")
