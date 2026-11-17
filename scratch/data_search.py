from pathlib import Path
import numpy as np
import trimesh
import json

p = "data/teeth3ds_sample/01F4JV8X/01F4JV8X_upper.obj"
obj_path = Path(p)

if not obj_path.exists():
    raise FileNotFoundError(f"{obj_path} doesnt exist")

json_path = obj_path.with_suffix(".json")  # grab json of obj

if not json_path.exists():
    raise FileNotFoundError(f"{json_path} doesnt exist")
with open(json_path) as f:
    data_dict = json.load(f)

print(data_dict.keys())  # get id, jaw, labels, instances

for key, value in data_dict.items():
    print(f"key: {key},  value type {type(value)}")
    if type(value) == list:  # see what the list values are
        print(f"value len: {len(value)} | first 10: {value[:10]}")

        a = np.asarray(value)
        print(
            f"{a.dtype} | {a.shape} | {np.unique(a)}"
        )  # labels with 1->upper right, 2->upper left, 3->lower left, 4->lower right
        # x8 is wisdom teeth
    else:
        print(value)
patient_id, jaw_type = obj_path.stem.split("_")
assert data_dict["id_patient"] == patient_id, (
    f"mismatched id: {data_dict['id_patient']} vs {patient_id}"
)
