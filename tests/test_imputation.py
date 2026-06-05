import random
from biv_lite import impute_biv_frames, BivFrames
from copy import deepcopy
from numpy import testing as npt
import numpy as np


def test_impute_biv_frames_preserves_non_imputed_frames(sample_biv: BivFrames):
    """
    Test that impute_biv_frames preserves BivMesh models for non-imputed frames.
    
    This test:
    1. Loads fitted models from fitted_models.txt
    2. Randomly removes 3 frames (makes them empty)
    3. Runs impute_biv_frames
    4. Verifies that non-imputed frames remain identical to the originals
    """
    # Load original models
    num_frames = len(sample_biv)
    
    # Randomly select 3 frames to remove
    frames_to_remove = set(random.sample(range(num_frames), 3))
    
    # Create a copy of models with 3 frames removed (made empty)
    imputed_models = deepcopy(sample_biv)
    imputed_models.make_frames_empty(frames_to_remove)

    # Validate that they are really empty
    for i in range(num_frames):
        if i not in frames_to_remove:
            npt.assert_array_equal(imputed_models[i], np.zeros((0, 3)))

    # Run imputation
    result_models = impute_biv_frames(imputed_models)
    assert result_models is not None
    
    # Verify that non-imputed frames remain identical
    for i in range(num_frames):
        if i not in frames_to_remove:
            # Non-imputed frames should be equivalent to originals 
            # This can be checked only from the control points
            npt.assert_array_equal(sample_biv[i].control_points, result_models[i].control_points)
    
    # Verify that previously empty frames are now filled
    for i in frames_to_remove:
        assert result_models[i].control_points.shape == (388, 3)
    
