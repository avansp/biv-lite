from biv_lite import BivMesh
from pathlib import Path
from typing import List
import re


class BivFrames(List[BivMesh]):
    """
    A class that handles multiple BivMesh frames as a full cardiac cycle.
    """
    @classmethod
    def from_folder(cls, folder: Path, pattern: str = "*_Model_Frame_*.txt", frame_str: str = r'_(\d+).txt'):
        biv = BivFrames()

        for i, input_file in enumerate(sorted(folder.glob(pattern), key=lambda p: int(re.search(frame_str, p.name).groups()[0]))):
            biv.append(BivMesh.from_fitted_model(input_file, name=f"frame_{i}"))

        return biv