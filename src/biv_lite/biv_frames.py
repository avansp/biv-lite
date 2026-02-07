from __future__ import annotations

from biv_lite import BivMesh
from pathlib import Path
from typing import List
import re
from collections.abc import Sequence
import numpy as np
from typing import Optional
import shutil


class BivFrames(Sequence):
    """
    Represents a collection of biventricular meshes across multiple frames. This class is a specialized
    sequence of BiV meshes, enabling operations and computations over a series of time frames of the
    heart model.

    The purpose of this class is to group and process multiple biventricular meshes (BiVMeshes) representing
    different time frames from cardiac imaging data. It provides methods for operations such as loading meshes
    from a directory, saving them, modifying frames, and calculating geometric or physiological properties like
    volumes and strain.

    Attributes:
        biv_mesh (List[BivMesh]): List of biventricular meshes representing heart models per frame.
        frames (list): List of frame identifiers corresponding to the BiVMeshes. Must match the number
            of biv_mesh elements.
    """
    def __init__(self, biv_mesh_list: List[BivMesh], frames: np.array = None):
        """
        A constructor for initializing an instance of the class with a list of BivMesh objects and
        optional frames. It populates metadata and ensures consistency between the number of
        frames and the biv_mesh list.

        Args:
            biv_mesh_list (List[BivMesh]): A list of BivMesh objects representing the meshes
                to be associated with the instance.
            frames (Optional[List[int]]): A list of integer frame indices corresponding to the
                BivMesh objects. If not provided, frames is initialized as a range equal to
                the length of `biv_mesh_list`.

        Raises:
            AssertionError: If the number of frames provided does not match the number of
                items in `biv_mesh_list`.
        """
        self.biv_mesh = biv_mesh_list
        if frames is None:
            self.frames = np.arange(len(self.biv_mesh))
        else:
            self.frames = frames

        assert self.frames.ndim == 1, "Frames must be a 1D array"
        assert len(self.frames) == len(self.biv_mesh), f"Invalid number of frames: {len(self.frames)}"

    @classmethod
    def from_folder(cls, folder: Path | str, pattern: str = "*_model_frame_*.txt", frame_str: str = r'_(\d+).txt', max_frames: int = None):
        """
        Parses text files matching a specific pattern within a folder and constructs a new BivFrames
        object based on extracted frame identifiers.

        This method scans a given folder for files matching the specified pattern. The file names
        are expected to have frame identifiers, which are extracted using the provided regular
        expression. The files are sorted in ascending order of the extracted frame numbers, then
        used to construct BivMesh objects. These objects are subsequently used to create and
        return a BivFrames instance.

        Args:
            folder (Path | str): Path to the directory containing the text files.
            pattern (str): File name pattern to search for. Defaults to "*_Model_Frame_*.txt".
            frame_str (str): Regular expression used to extract frame numbers from file names.
            max_frames (int): Maximum number of frames. Useful if you know there should be N number of frames but missing files at the end of the cycles.

        Returns:
            BivFrames: A new instance of BivFrames containing BivMesh objects created from
                the matched files.

        Raises:
            ValueError: If the frame numbers cannot be extracted or are not in the expected format.
        """
        bivs = []

        for i, input_file in enumerate(sorted(Path(folder).glob(pattern), key=lambda p: int(re.search(frame_str, p.name).groups()[0]))):
            bivs.append(BivMesh.from_fitted_model(input_file, name=f"frame_{i}"))

        # add empty frames if len(bivs) < max_frames
        n = len(bivs)
        if (max_frames is not None) and (n < max_frames):
            for i in range(max_frames - n):
                bivs.append(BivMesh(control_points=np.zeros((0, 3)), name=f"frame_{n + i}"))
                            
        return BivFrames(bivs)
        

    def save_as(self, model_name: str, new_folder: Path | str, overwrite: bool = False) -> None:
        """
        Saves the current state of the object as a set of files in the specified folder with
        the given model name. The files are created in a format specific to fitted models,
        where each file represents a frame of the model. The method ensures that the target
        folder is created if it does not already exist.

        Args:
            model_name: The base name of the output files to be saved. Each file will have
                a unique suffix associated with its frame index.
            new_folder: The path to the folder where the files will be saved. If the folder
                does not exist, it will be created.
            overwrite: Ignore existing files if the new folder exists
        """
        new_folder = Path(new_folder)
        if new_folder.exists() and overwrite:
            # delete the new_folder
            shutil.rmtree(new_folder)

        new_folder.mkdir(parents=True, exist_ok=False)
        for i, b in enumerate(self.biv_mesh):
            b.to_fitted_model(new_folder / f"{model_name}_model_frame_{i:03d}.txt", i)

    def drop_empty_frames(self, in_place: bool = False) -> Optional[BivFrames]:
        """
        Filters out empty frames from the object by checking the `biv_mesh` attribute.
        It can update the instance in-place or return a new instance with the filtered frames.

        Args:
            in_place: A boolean value. If True, modifies the instance in-place.
                If False, returns a new instance with non-empty frames.

        Returns:
            Optional[BivFrames]: A new instance with non-empty frames if `in_place` is False.
                Otherwise, returns None.
        """
        valid_idx = np.array([i for i, b in enumerate(self.biv_mesh) if not b.is_empty()])
        new_frames = self.frames[valid_idx]

        if in_place:
            self.frames = new_frames
            self.biv_mesh = [self.biv_mesh[i] for i in valid_idx]
            return None
        else:
            return BivFrames(biv_mesh_list=[self.biv_mesh[i] for i in valid_idx], frames = new_frames)

    def make_frames_empty(self, i_frames: List[int] | np.array):
        """
        Updates the control points of selected frames to empty arrays. This function takes
        a list or array of frame indices and sets their corresponding control points in the
        `biv_mesh` attribute to an empty NumPy array with a shape of (0, 3).

        Args:
            i_frames: List or array of integers representing the indices of frames
                within the `biv_mesh` attribute for which the control points will be
                reset.
        """
        for i in i_frames:
            self.biv_mesh[i].control_points = np.zeros((0, 3))

    @classmethod
    def from_control_points(cls, control_points: np.array):
        """
        Creates an instance of `BivFrames` object from the provided control points. The control points
        are expected to be a 3D array where each frame of the array represents a single 3D BivMesh
        configuration with a specific name. The function validates the shape of the input to ensure
        it adheres to specified constraints. If validation passes, it constructs a list of
        `BivMesh` objects for each frame and uses them to create the target `BivFrames` composite object.

        Args:
            control_points (np.array): A 3D NumPy array with shape (388, 3, nframes), where nframes is
                the number of frames. Each frame is a 3-dimensional representation of the control
                points utilized for creating BivMesh instances.

        Returns:
            BivFrames: A `BivFrames` object containing a list of `BivMesh` objects, one for each frame.

        Raises:
            AssertionError: If the number of control points is not 388.
            AssertionError: If the dimension of control points is not 3.
            AssertionError: If the number of frames is less than or equal to 0.
        """
        npts, dim, nframes = control_points.shape
        assert npts == 388, f"The number of control points must equal to 388"
        assert dim == 3, f"The dimension of control points must equal to 3"
        assert nframes > 0, f"The number of frames must be greater than 0"

        bivs = []
        for i in range(nframes):
            bivs.append(BivMesh(control_points[:,:,i], name=f"frame_{i}"))

        return BivFrames(bivs)

    def is_normalised_time(self) -> bool:
        """
        Checks if all time values in 'frames' are normalized.

        A normalized time value means it falls within the range [0, 1). This method
        iterates through the 'frames' attribute and ensures that all values meet
        this criterion. The 'frames' attribute should be iterable, containing
        numeric values for comparison. This function does not modify the state of
        the object.

        Returns:
            bool: True if all time values in 'frames' are normalized, False
            otherwise.
        """
        return all(0 <= t < 1.0 for t in self.frames)

    def __getitem__(self, item):
        """
        Retrieves an item or slice from the internal data structure.

        Retrieves a BivFrame or a slice of BivFrames from the internal biv_mesh
        data, depending on whether the provided index is a single element or
        a slice.

        Args:
            item: An index or slice specifying the position of the item(s) to
                retrieve.

        Returns:
            BivMesh: A single BivMesh object if the index is a singular element.
            BivFrames: A BivFrames object containing a slice of BivMesh objects
                and frames if the index is a slice.
        """
        # This is the difference with ordinary list because we want to return BivFrames if item is a slice.
        # Otherwise just a BivMesh object.
        if isinstance(item, slice):
            return BivFrames(self.biv_mesh[item], frames=self.frames[item])
        else:
            return self.biv_mesh[item]

    def __len__(self):
        return len(self.biv_mesh)

    def __iter__(self):
        return iter(self.biv_mesh)

    def lv_endo_volumes(self):
        """
        Calculates left ventricular (LV) endocardial volumes for each biventricle mesh.

        This function iterates through a list of biventricle meshes and calculates
        the LV endocardial volume for each individual mesh. The result is a list of
        volumes, where each volume corresponds to the LV endocardial volume of a mesh
        in the `biv_mesh` list.

        Returns:
            list of float: A list containing the LV endocardial volumes for each
            biventricle mesh in the `biv_mesh` attribute.
        """
        vols = []
        for b in self.biv_mesh:
            vols.append(b.lv_endo_volume())

        return vols

    def volumes(self, mass_index: float = 1.05) -> dict:
        """
        Calculates and returns volumes and masses for different regions of a bi-ventricular
        mesh. This includes endocardial and epicardial volumes for the left and right
        ventricles, as well as their respective masses scaled by an optional mass index.

        Args:
            mass_index (float): A scaling factor for computing the masses from the
                differences in epicardial and endocardial volumes. Default is 1.05.

        Returns:
            dict: A dictionary containing the calculated structures:
                'LV_ENDO': List of left ventricular endocardial volumes.
                'LV_EPI': List of left ventricular epicardial volumes.
                'RV_ENDO': List of right ventricular endocardial volumes.
                'RV_EPI': List of right ventricular epicardial volumes.
                'LVM': List of left ventricular masses scaled by the mass index.
                'RVM': List of right ventricular masses scaled by the mass index.
        """
        lv_endo = []
        lv_epi = []
        rv_endo = []
        rv_epi = []

        for b in self.biv_mesh:
            lv_endo.append(b.lv_endo_volume())
            lv_epi.append(b.lv_epi_volume())
            rv_endo.append(b.rv_endo_volume())
            rv_epi.append(b.rv_epi_volume())

        lv_mass = [mass_index * (epi - endo) for endo, epi in zip(lv_endo, lv_epi)]
        rv_mass = [mass_index * (epi - endo) for endo, epi in zip(rv_endo, rv_epi)]

        return {
            'Frame': list(range(len(lv_endo))),
            'LV_ENDO': lv_endo, 'LV_EPI': lv_epi, 
            'RV_ENDO': rv_endo, 'RV_EPI': rv_epi,
            'LVM': lv_mass, 'RVM': rv_mass }
    
    def gls(self, ed_frame: int):
        """Compute global longitudinal strain values."""
        gls_vs = [('LV', '2CH'), ('LV', '4CH'), ('RVS', '4CH'), ('RVFW', '4CH')]

        # collect arc lengths for the combination of views & surfaces
        arcs = {f"{s}_GLS_{v}": np.array([b.long_arc_length(v, s) for b in self.biv_mesh]) for s, v in gls_vs}

        # compute the strain
        strain = {k: (v - v[ed_frame]) / v[ed_frame] for k, v in arcs.items()}

        return strain

    def gcs(self, ed_frame: int):
        """Compute global circumferential strain values."""
        gcs_vs = [('LV', 'APEX'), ('LV', 'MID'), ('LV', 'BASE'),
                  ('RVFW', 'APEX'), ('RVFW', 'MID'), ('RVFW', 'BASE'),
                  ('RVS', 'APEX'), ('RVS', 'MID'), ('RVS', 'BASE')]

        # collect arc lengths for the combination of views & surfaces
        arcs = {f"{s}_GCS_{v}": np.array([b.circ_arc_length(v, s) for b in self.biv_mesh]) for s, v in gcs_vs}

        # compute the strain
        strain = {k: (v - v[ed_frame]) / v[ed_frame] for k, v in arcs.items()}

        return strain

