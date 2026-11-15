from pathlib import Path
import numpy as np
import trimesh
import json
from dataclasses import dataclass


@dataclass
class MeshData:
    mesh: trimesh.Trimesh
    labels: np.ndarray
    instances: np.ndarray


def load_scan(path: Path | str) -> MeshData:
    """Load the scan and its labels + instances from the json file.

    Args:
        path (Path | str): The path to the scan file. str or Path object. The file should be a .obj file.

    Returns:
        MeshData: The loaded mesh data.

    Raises:
        FileNotFoundError: If the scan file or its corresponding json file does not exist.
        AssertionError: If the patient ID or jaw type in the json file does not match the scan file name.

    """
    obj_path = Path(path)

    if not obj_path.exists():
        raise FileNotFoundError(f"{obj_path} doesnt exist")

    json_path = obj_path.with_suffix(".json")  # grab json of obj

    if not json_path.exists():
        raise FileNotFoundError(f"{json_path} doesnt exist")
    with open(json_path) as f:
        data_dict = json.load(f)
    patient_id, jaw_type = obj_path.stem.split("_")  # grab jaw and patient
    assert data_dict["id_patient"] == patient_id, (
        f"mismatched id: {data_dict['id_patient']} vs {patient_id}"
    )
    assert data_dict["jaw"] == jaw_type, (
        f"mismatched jaw: {data_dict['jaw']} vs {jaw_type}"
    )

    labels = np.asarray(data_dict["labels"], dtype=np.int64)  # grab labels
    instances = np.asarray(data_dict["instances"], dtype=np.int64)  # grab instances
