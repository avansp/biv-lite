from biv_lite import BivFrames


def test_bivframes_empty_frames(sample_biv: BivFrames):
    n = len(sample_biv)

    # make frame 3 empty
    sample_biv.make_frames_empty([3])
    assert sample_biv[3].is_empty()

    # make frame 5, 8, 10 empy
    sample_biv.make_frames_empty([5, 8, 10])
    assert all([sample_biv[i].is_empty() for i in [5, 8, 10]])

    # drop empty returns a new object
    new_biv = sample_biv.drop_empty_frames(in_place=False)
    assert len(new_biv) == (n-4)
    assert len(new_biv) == len(new_biv.frames)
    assert all([not b.is_empty() for b in new_biv])
    assert all([sample_biv[i].is_empty() for i in [5, 8, 10]])
    assert len(sample_biv) == n

    # drop empty in place
    sample_biv.drop_empty_frames(in_place=True)
    assert len(sample_biv) == n-4
    assert len(sample_biv.frames) == n-4
    assert all([not b.is_empty() for b in sample_biv])
