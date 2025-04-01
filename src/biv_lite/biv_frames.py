from biv_lite import BivMesh
from pathlib import Path
from typing import List
import re


class BivFrames(List[BivMesh]):
    """
    This simply a list of BivMesh objects with some extra functions specific for cardiac motion.
    """
    @classmethod
    def from_folder(cls, folder: Path | str, pattern: str = "*_Model_Frame_*.txt", frame_str: str = r'_(\d+).txt'):
        biv = BivFrames()

        for i, input_file in enumerate(sorted(Path(folder).glob(pattern), key=lambda p: int(re.search(frame_str, p.name).groups()[0]))):
            biv.append(BivMesh.from_fitted_model(input_file, name=f"frame_{i}"))

        return biv

    def gls(self):
        """Compute global longitudinal strain values."""
        # TODO: complete this by copying codes frm biv-me's calculate_longitudinal_strain
