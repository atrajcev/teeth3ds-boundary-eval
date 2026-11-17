import trimesh
import numpy as np
from load_scan import load_scan
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
