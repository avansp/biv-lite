from biv_lite import BivFrames, BivMesh
import numpy as np
from scipy.interpolate import make_splprep
import copy


class BivParametric:
    """
    Represents a parametric model for interpolating and generating a smooth representation
    of `BivFrames` over a normalized time frame.

    The class utilizes spline interpolation techniques to generate either individual
    `BivMesh` objects or a sequence of `BivMesh` objects encapsulated in a `BivFrames`
    object. Smoothness and order of interpolation can be customized during initialization.

    Attributes:
        biv_frames (BivFrames): A deep copy of the input `BivFrames`, representing the control
            points for the parametric model. The normalized time frames are adjusted based on
            the input or auto-generated values.
        funcs_int (list): List of spline interpolation functions for generating control points
            based on the normalized time parameter. Each function corresponds to a control
            point across frames.
    """
    def __init__(self, biv_frames: BivFrames, t: list[float] = None, k: int = 3, smoothing = 0):
        """
        Initializes a class instance with a set of BivFrames and generates their parametric
        representation over a normalized time frame. The parametric representation ensures smooth
        interpolation between the control points of the frames, with customizable smoothing and
        order.

        Args:
            biv_frames (BivFrames): A sequence of BivFrames representing the control points to
                interpolate. Must contain more than three frames.
            t (list[float], optional): A monotonically increasing normalized time list with values
                0.0 <= t < 1.0, corresponding to the BivFrames. Length of `t` must match the length
                of `biv_frames`. If not provided, will be auto-generated.
            k (int, optional): The degree of the spline functions used for interpolation (order of the curves).
            smoothing (float, optional): Smoothness factor for the interpolation. A higher value
                decreases fidelity to the control points.

        Raises:
            AssertionError: If the length of `biv_frames` is less than or equal to 3.
            AssertionError: If the length of `t` does not match the number of `biv_frames`.
            AssertionError: If `t` is not a monotonically increasing sequence.
            AssertionError: If `t` contains values outside the range [0.0, 1.0).
        """
        self.biv_frames = copy.deepcopy(biv_frames)
        assert len(self.biv_frames) > 3, f"Not enough frames to create parametric BivFrames"

        # create the normalised time frame
        if t is not None:
            assert len(t) == len(biv_frames), "Invalid length between biv_frames and t"
            assert all(0 <= ti < 1.0 for ti in t), "Values of t must 0.0 <= t < 1.0"
            assert all(ti < tj for ti, tj in zip(t, t[1:])), "Values of t is not monotically increasing"
            self.biv_frames.frames = t
        else:
            ts = np.linspace(0.0, 1.0, num=len(biv_frames)+1)
            self.biv_frames.frames = ts[:-1]

        assert self.biv_frames.is_normalised_time()

        # missing values create problem during interpolation
        self.biv_frames.drop_empty_frames(in_place=True)

        # create time axis
        tn = self.biv_frames.frames
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
            f_int, _ =  make_splprep(xs, u = ts, s = smoothing)
            self.funcs_int.append(f_int)

    def __call__(self, t):
        """
        Callable object that generates either a `BivMesh` or a `BivFrames` object
        from the provided time parameter `t`. This functionality is contingent on
        whether `t` is a scalar or an array.

        If `t` is a scalar, the method validates that it is in the range [0, 1],
        then generates a `BivMesh` by applying a sequence of functions stored
        in `self.funcs_int` to `t`.

        If `t` is an array, the method verifies all values are within [0, 1],
        then generates a `BivFrames` object. For each time point in the array,
        it creates a `BivMesh` by applying the functions in `self.funcs_int`.

        Args:
            t (Union[float, np.ndarray]): Time parameter to generate the mesh or
                frame objects. For single frames, pass a scalar value in the
                range [0, 1]. For multiple frames, pass a NumPy array where each
                element represents a valid time point in the range [0, 1].

        Returns:
            Union[BivMesh, BivFrames]: A single `BivMesh` if `t` is a scalar, or
            a `BivFrames` object containing multiple `BivMesh` instances if `t`
            is an array.

        Raises:
            AssertionError: If `t` (or any of its elements when it is an array)
            is not in the valid range [0, 1].
        """
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
