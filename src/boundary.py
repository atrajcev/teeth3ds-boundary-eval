import trimesh
import numpy as np
from load_scan import load_scan
import scipy.spatial
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

def peel_rings(mesh,labels,tooth,k):
    """Peel k rings of vertices from the boundary of a tooth.

    Args:
        mesh (trimesh.Trimesh): The mesh to peel.
        label (np.ndarray): The labels for each vertex.
        tooth (int): The tooth id to peel.
        k (int): The number of rings to peel.
    """
    pred = labels.copy()
    for _ in range(k):
        ring = boundary_vertices(mesh, pred, tooth)
        pred[ring] = 0
    return pred

def dice(true,pred,tooth):
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

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Find boundary vertices of a tooth"
    )
    parser.add_argument(
        "path",
        type=str,
        help="The path to the scan file. The file should be a .obj file.",
    )
    parser.add_argument(
        "--tooth",
        type=int,
        help="Tooth id to evaluate",
        default = 11,
    )
    args = parser.parse_args()
    mesh_data = load_scan(args.path)
    boundary_v = boundary_vertices(mesh_data.mesh, mesh_data.labels, args.tooth)
    print(f"Boundary vertices count: {len(boundary_v)}, tooth total vertices: {(mesh_data.labels==args.tooth).sum()}")
    peel_1 = peel_rings(mesh_data.mesh, mesh_data.labels, args.tooth, 1)
    dice_score = dice(mesh_data.labels, peel_1, args.tooth)
    
    print(f"After peeling 1 ring, tooth total vertices for tooth {args.tooth}: {(peel_1==args.tooth).sum()}")
    print(f"Dice score after peeling 1 ring for tooth {args.tooth}: {dice_score:.4f}")

