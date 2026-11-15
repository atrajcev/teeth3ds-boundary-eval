"""
Load a scan and its labels + instances from the json file.

    Example usage:
        python src/load_scan.py data/teeth3ds_sample/01F4JV8X/01F4JV8X_upper.obj

    Example output:
        Loaded scan: data/teeth3ds_sample/01F4JV8X/01F4JV8X_upper.obj
        Patient ID: 01F4JV8X
        Jaw type: upper
        Number of vertices: 120522
        Number of faces: 240900
        Number of labels: 120522
        Number of instances: 120522
        Number of orphaned vertices: 0

    Author: Aleksander Trajcevski
"""

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
    patient_id: str
    jaw_type: str
    orphaned_vertices: np.ndarray


def load_scan(path: Path | str) -> MeshData:
    """Load the scan and its labels + instances from the json file.

    Args:
        path (Path | str): The path to the scan file. str or Path object. The file should be a .obj file.

    Returns:
        MeshData: The loaded mesh data.

    Raises:
        FileNotFoundError: If the scan file or its corresponding json file does not exist.
        AssertionError: If the patient ID or jaw type in the json file does not match the scan file name.
        ValueError: If the number of labels or instances does not match the number of vertices in the mesh, or if the labels are out of range, or if trimesh reordered the vertices, or if trimesh converted from 1-based index to 0-based.
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

    raw_xyz = read_obj_vertices(
        obj_path
    )  # read vertices from obj as reference check against mesh
    mesh = trimesh.load_mesh(
        obj_path, process=False
    )  # load mesh to check for errors, process = False to avoid trimesh trying to fix the mesh, labels could reorder due to merges

    labels = np.asarray(data_dict["labels"], dtype=np.int64)  # grab labels
    instances = np.asarray(data_dict["instances"], dtype=np.int64)  # grab instances
    # vertex count matches label count, if not, something is wrong with the scan or the labels
    if len(labels) != len(mesh.vertices):
        raise ValueError(
            f"mismatched lengths: labels = {len(labels)} vs vertices = {len(mesh.vertices)}"
        )
    # vertex count matches instance count, if not, something is wrong with the scan or the instances
    if len(instances) != len(mesh.vertices):
        raise ValueError(
            f"mismatched lengths: instances = {len(instances)} vs vertices = {len(mesh.vertices)}"
        )
    # labels should be 0 for gums and quadrants 1-8 and position 1-8 for adult and baby teeth, if not, something is wrong with the labels
    quadrants = labels // 10
    positions = labels % 10
    is_gum = labels == 0
    is_tooth = (1 <= quadrants) & (quadrants <= 8) & (1 <= positions) & (positions <= 8)
    valid = is_gum | is_tooth
    if not valid.all():
        raise ValueError(
            f"labels out of range: {np.unique(labels[~valid])}"
        )  # print invalid labels
    # check if count of raw xyz matches mesh vertices
    if len(raw_xyz) != len(mesh.vertices):
        raise ValueError(
            f"mismatched lengths: raw_xyz (file) = {len(raw_xyz)} vs vertices (trimesh) = {len(mesh.vertices)}"
        )
    # check if trimesh reordered the vertices, if so, something is wrong with the scan or the labels, 1e-6 is a small tolerance between floating point noise and scanner accuracy 0.01mm
    if not np.allclose(raw_xyz, mesh.vertices, atol=1e-6):
        raise ValueError(
            "trimesh reordered the vertices, something is wrong with the scan or the labels"
        )
    # check if trimesh converted from 1-based index to 0-based or if faces out of range
    if np.min(mesh.faces) != 0 or np.max(mesh.faces) > len(mesh.vertices) - 1:
        raise ValueError(
            f"trimesh not ordered 0 to N-1. min = {np.min(mesh.faces)}, max = {np.max(mesh.faces)}, vertices (N-1) = {len(mesh.vertices) - 1}"
        )
    used_vertices = np.unique(mesh.faces)  # grab unique vertices used in faces
    orphaned_vertices = np.setdiff1d(
        np.arange(len(mesh.vertices)), used_vertices
    )  # grab vertices not used in faces
    return MeshData(
        mesh=mesh,
        labels=labels,
        instances=instances,
        patient_id=patient_id,
        jaw_type=jaw_type,
        orphaned_vertices=orphaned_vertices,
    )


def read_obj_vertices(path: Path | str) -> np.ndarray:
    """Read the vertices from an .obj file.

    Args:
        path (Path | str): The path to the .obj file. str or Path object.

    Returns:
        np.ndarray: The vertices of the mesh as a numpy array of shape (N, 3).

    Raises:
        FileNotFoundError: If the .obj file does not exist.
    """
    obj_path = Path(path)

    if not obj_path.exists():
        raise FileNotFoundError(f"{obj_path} doesnt exist")
    vertices = []
    for line in obj_path.read_text().splitlines():
        if line.startswith("v "):  # vertex line
            vertices.append(
                [float(v) for v in line.split()[1:4]]
            )  # grab x,y,z coordinates
    vertices = np.array(vertices, dtype=np.float64)
    return vertices


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Load a scan and its labels + instances from the json file."
    )
    parser.add_argument(
        "path",
        type=str,
        help="The path to the scan file. The file should be a .obj file.",
    )
    args = parser.parse_args()
    mesh_data = load_scan(args.path)
    print(f"Loaded scan: {args.path}")
    print(f"Patient ID: {mesh_data.patient_id}")
    print(f"Jaw type: {mesh_data.jaw_type}")
    print(f"Number of vertices: {len(mesh_data.mesh.vertices)}")
    print(f"Number of faces: {len(mesh_data.mesh.faces)}")
    print(f"Number of labels: {len(mesh_data.labels)}")
    print(f"Number of instances: {len(mesh_data.instances)}")
    print(f"Number of orphaned vertices: {len(mesh_data.orphaned_vertices)}")
