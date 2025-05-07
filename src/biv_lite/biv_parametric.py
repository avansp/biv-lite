from biv_lite import BivFrames, BivMesh
import numpy as np
from scipy.interpolate import make_splprep


class BivParametric:
    """BivFrames defined as a parametric function of 0.0 <= t < 1.0 that defines a full cardiac cycle.

    """
    def __init__(self, biv_frames: BivFrames, t: list[float] = None, k: int = 3):
        self.metadata = dict()
        self.biv_frames = biv_frames
        assert len(self.biv_frames) > 3, f"Not enough frames to create parametric BivFrames"

        # create the normalised time frame
        if t is not None:
            assert len(t) == len(biv_frames), "Invalid length between biv_frames and t"
            assert all(0 <= ti < 1.0 for ti in t), "Values of t must 0.0 <= t < 1.0"
            assert all(ti < tj for ti, tj in zip(t, t[1:])), "Values of t is not monotically increasing"
            self.metadata["normalised_time"] = t
        else:
            ts = np.linspace(0.0, 1.0, num=len(biv_frames)+1)
            self.metadata["normalised_time"] = ts[:-1]

        # check frames values
        if min(self.biv_frames.frames) < 0.0 or max(self.biv_frames.frames) >= 1.0:
            # normalising the frames
            self.biv_frames.frames = np.linspace(0, 1.0, len(self.biv_frames) + 1)
            self.biv_frames.frames = self.biv_frames.frames[:-1]

        # create time axis
        tn = self.metadata["normalised_time"]
        ts = np.concat((tn[-k:] - 1.0, tn, 1.0 + tn[:k]))
        # ts = np.concat((self.biv_frames.frames[-k:] - 1.0, self.biv_frames.frames, 1.0 + self.biv_frames.frames[:k]))

        # create interpolation functions for each control point
        self.funcs_int = []
        n_ctrl_pts = self.biv_frames[0].control_points.shape[0]
        for c in range(n_ctrl_pts):
            # collect control points
            ctrl_pts = np.vstack([self.biv_frames[i].control_points[c, :] for i in range(len(self.biv_frames))])

            # prepend and append k samples
            xs = np.transpose(np.vstack((ctrl_pts[-k:], ctrl_pts, ctrl_pts[:k])))

            # create interpolation function
            f_int, _ =  make_splprep(xs, u = ts)
            self.funcs_int.append(f_int)

    def __call__(self, t):
        if np.isscalar(t):
            # this should return a BivMesh
            assert 0 <= t <= 1.0, f"Invalid time frame {t}"
            return BivMesh(np.vstack([f(t) for f in self.funcs_int]), name=f"t={t:.2f}")
        else:
            # this should return a BivFrames
            t = np.array(t)
            assert all(np.logical_and(t >= 0, t <= 1.0)), f"Invalid time frame {t}"

            biv_mesh_list = np.stack([f(t) for f in self.funcs_int])
            return BivFrames([BivMesh(biv_mesh_list[:,:,i]) for i in range(biv_mesh_list.shape[2])], frames=t)
