import trimesh
import numpy as np
from load_scan import load_scan
import scipy.spatial
import pandas as pd
from pathlib import Path
def boundary_vertices(mesh, labels, tooth) -> np.ndarray:
    edges = mesh.edges_unique
    vertex_a = edges[:,0]
    vertex_b = edges[:,1]
    la = labels[vertex_a] #first vertex of edge   
    lb = labels[vertex_b] #second vertex
    in_a = la==tooth
    in_b = lb==tooth
    crossing = (in_a) != (in_b)
    tooth_end = np.where(in_a,vertex_a, vertex_b)
    return np.unique(tooth_end[crossing])

def peel_rings(mesh,labels,tooth,k) -> np.ndarray:
    """Peel k rings of vertices from the boundary of a tooth.

    Args:
        mesh (trimesh.Trimesh): The mesh to peel.
        labels (np.ndarray): The labels for each vertex.
        tooth (int): The tooth id to peel.
        k (int): The number of rings to peel.
    Returns:
        np.ndarray: The labels after peeling k rings of vertices from the boundary of the tooth.
    """
    pred = labels.copy()
    for _ in range(k):
        ring = boundary_vertices(mesh, pred, tooth)
        pred[ring] = 0
    return pred

def dice(true,pred,tooth) -> float:
    """Compute the dice score for a tooth.

    Args:
        true (np.ndarray): The ground truth labels.
        pred (np.ndarray): The predicted labels.
        tooth (int): The tooth id to compute the dice score for.
    Returns:
        float: The dice score for the tooth.
    """
    true_mask = true==tooth
    pred_mask = pred==tooth
    intersection = np.sum(true_mask & pred_mask)
    dice_score = 2 * intersection / (np.sum(true_mask) + np.sum(pred_mask))
    return dice_score

def boundary_shift_mm(mesh,true,pred,tooth) -> tuple[float,float,float]:
    """Compute the median, p95 and max boundary shift in mm for a tooth.

    Args:
        mesh (trimesh.Trimesh): The mesh to compute the boundary shift on.
        true (np.ndarray): The ground truth labels.
        pred (np.ndarray): The predicted labels.
        tooth (int): The tooth id to compute the boundary shift for.
    Returns:
        float: The median boundary shift in mm for the tooth.
        float: the p95 boundary shift in mm for the tooth
        float: max dist in mm for the tooth
    """
    true_boundary = boundary_vertices(mesh,true,tooth)
    pred_boundary = boundary_vertices(mesh,pred,tooth)
    tree = scipy.spatial.cKDTree(mesh.vertices[true_boundary])
    dist, _ = tree.query(mesh.vertices[pred_boundary])
    return np.median(dist), np.percentile(dist,95), dist.max()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Find boundary vertices of a tooth"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="The path to the scan file. The file should be a .obj file.",
    )
    parser.add_argument(
        "--tooth",
        type=int,
        help="Tooth id to evaluate",
        default = 11,
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None
    )
    args = parser.parse_args()
    if args.out is None:
        args.out = f"results/boundary_stats_{args.tooth}.csv"
    mesh_data = load_scan(args.path)
    if not np.any(mesh_data.labels==args.tooth):
        raise ValueError(f"{args.tooth} tooth is missing in scan")
    boundary_v = boundary_vertices(mesh_data.mesh, mesh_data.labels, args.tooth)
    print(f"Boundary vertices count: {len(boundary_v)}, tooth total vertices: {(mesh_data.labels==args.tooth).sum()}")
    
    rows=[]
    for i in range(4):
        pred = peel_rings(mesh_data.mesh, mesh_data.labels, args.tooth, i)
        dice_score = dice(mesh_data.labels, pred, args.tooth)
        med,p95,mx=boundary_shift_mm(mesh_data.mesh, mesh_data.labels, pred,args.tooth)
        rows.append({"tooth": args.tooth, "peeled_rings": i, "total_vertices_after_peel":(pred==args.tooth).sum(), "dice_score": dice_score, "median_shift":med, "p95_shift":p95,"max_shift":mx})
    df = pd.DataFrame(rows)
    print(df)
    to_csv_path = Path(args.out)
    to_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(to_csv_path, index=False)

