from load_scan import load_scan, MeshData
from pathlib import Path
import numpy as np
import pandas as pd

def scan_stats(data: MeshData) -> dict:
    """Compute statistics for a scan.

    Args:
        data (MeshData): The loaded mesh data.

    Returns:
        dict: A dictionary containing the statistics of the scan.
        output keys:
            - patient_id: str, the patient ID
            - jaw_type: str, the jaw type (upper or lower)
            - num_teeth: int, the number of unique teeth (labels excluding 0)
            - num_vertices: int, the number of vertices in the mesh
            - num_faces: int, the number of faces in the mesh
            - num_orphaned_vertices: int, the number of orphaned vertices in the mesh
            - edge_length_median: float, the median length of unique edges in the mesh
            - edge_length_p95: float, the 95th percentile length of unique edges in the mesh
            - bounding_box_x: float, the size of the bounding box in the x dimension
            - bounding_box_y: float, the size of the bounding box in the y dimension
            - bounding_box_z: float, the size of the bounding box in the z dimension
    """
    edge_lengths = data.mesh.edges_unique_length
    bb_x, bb_y, bb_z = data.mesh.bounding_box.extents
    stats = {
        "patient_id": data.patient_id,
        "jaw_type": data.jaw_type,
        "num_teeth": len(np.unique(data.labels[data.labels!=0])), #unique labels excluding 0 (gums)
        "num_vertices": len(data.mesh.vertices),
        "num_faces": len(data.mesh.faces),
        "num_orphaned_vertices": len(data.orphaned_vertices),
        "edge_length_median": np.median(edge_lengths), # len of each unique edge, median of all edges
        "edge_length_p95": np.percentile(edge_lengths, 95), # len of each unique edge, p95 of all edges
        "bounding_box_x": bb_x,
        "bounding_box_y": bb_y,
        "bounding_box_z": bb_z, # size of bounding box in x,y,z
    }

    return stats


def collect_stats(path: Path | str) -> tuple[pd.DataFrame, list[tuple[Path, str]], set[int]]:
    """Collect statistics for all scans in a directory.
    Args:
        path (Path | str): The path to the directory containing the scan files
    Returns:
        tuple[pd.DataFrame, list[tuple[Path, str]], set[int]]:
            - pd.DataFrame: A DataFrame containing the statistics for each scan
            - list[tuple[Path, str]]: A list of tuples containing the path to the scan file and the error message for any scans that failed to load
            - set[int]: A set of all unique labels found across all scans
    
    """
    path = Path(path)
    if not Path(path).is_dir():
                raise ValueError(f"{path} is not a directory")
    rows = []
    failures = []
    all_labels = set()
    obj_files = sorted(path.glob("**/*.obj"))
    if not obj_files:
        raise ValueError(f"No .obj files found in {path}")
    for obj_file in obj_files: #read sorted rows of obj files
        try:
            data = load_scan(obj_file)
        except Exception as e:
            failures.append((obj_file, str(e))) #store failed scans with error message
            continue
        stats = scan_stats(data)
        rows.append(stats)
        all_labels.update(np.unique(data.labels).tolist()) #store all unique labels found across all scans

    return pd.DataFrame(rows), failures, all_labels

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Collect statistics for all scans in a directory."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="The path to the directory containing the scan files.",
    )
    parser.add_argument(
            "--out",
            type=Path,
            help="The path to where the output CSV file will be saved.",
            default="results/scan_stats.csv"
            
        )
    
    args = parser.parse_args()
    path = args.path
    
    df, failures, all_labels = collect_stats(path)
    to_csv_path = args.out
    to_csv_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(to_csv_path, index=False)
    print(df.head())
    print(len(df), "rows written to", to_csv_path)
    print(f"Total scans processed: {len(df) + len(failures)}")
    print(df.describe())
    print(f"Failures: {failures}")
    print(f"All labels: {sorted(all_labels)}")