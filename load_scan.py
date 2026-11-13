from pathlib import Path
import numpy as np
import trimesh
import json


def load_scan(path):
    obj_path = Path(path)

    if not obj_path.exists():
        raise FileNotFoundError(f"{obj_path } doesnt exist")

    json_path = obj_path.with_suffix(".json") #grab json of obj

    if not json_path.exists():
        raise FileNotFoundError(f"{json_path} doesnt exist")
    with open(json_path) as f:
        data_dict = json.load(f)
    patient_id, jaw_type = obj_path.stem.split("_") #grab jaw and patient
    assert data_dict['id_patient'] == patient_id, f"mismatched id: {data_dict['id_patient']} vs {patient_id}"
