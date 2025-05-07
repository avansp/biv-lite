from biv_lite import BivMesh
from pathlib import Path
from typing import List
import re
from collections.abc import Sequence


class BivFrames(Sequence):
    """
    This simply a list of BivMesh objects with some extra functions specific for cardiac motion.
    """
    def __init__(self, biv_mesh_list: List[BivMesh], frames = None):
        self.metadata = dict()
        self.biv_mesh = biv_mesh_list
        if frames is None:
            self.frames = list(range(len(self.biv_mesh)))
        else:
            self.frames = frames

        assert len(self.frames) == len(self.biv_mesh), f"Invalid number of frames: {len(self.frames)}"

    @classmethod
    def from_folder(cls, folder: Path | str, pattern: str = "*_Model_Frame_*.txt", frame_str: str = r'_(\d+).txt'):
        bivs = []

        for i, input_file in enumerate(sorted(Path(folder).glob(pattern), key=lambda p: int(re.search(frame_str, p.name).groups()[0]))):
            bivs.append(BivMesh.from_fitted_model(input_file, name=f"frame_{i}"))

        return BivFrames(bivs)

    def __getitem__(self, item):
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
        """Just compute LV endo volumes"""
        vols = []
        for b in self.biv_mesh:
            vols.append(b.lv_endo_volume())

        return vols

    def volumes(self) -> dict:
        """Compute endo- and epicardial LV and RV volumes."""
        lv_endo = []
        lv_epi = []
        rv_endo = []
        rv_epi = []

        for b in self.biv_mesh:
            lv_endo.append(b.lv_endo_volume())
            lv_epi.append(b.lv_epi_volume())
            rv_endo.append(b.rv_endo_volume())
            rv_epi.append(b.rv_epi_volume())

        return { 'LV_ENDO': lv_endo, 'LV_EPI': lv_epi, 'RV_ENDO': rv_endo, 'RV_EPI': rv_epi }

    def gls(self):
        """Compute global longitudinal strain values."""
        # TODO: complete this by copying codes frm biv-me's calculate_longitudinal_strain
