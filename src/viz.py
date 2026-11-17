import numpy as np
import trimesh
import matplotlib
ALL_CODES = [ #make nested list of all possible codes, 1-8 for each quadrant and position
        quadrant*10 + position
        for quadrant in range(1,5) #teeth3ds has only 4 quadrants, 1-4 for upper right, upper left, lower left, lower right, no baby teeth, but we can still use 1-8 for each quadrant to be consistent with the labels
        for position in range(1,9)
]
ALL_CODES = np.array([0] + ALL_CODES)
def color_by_label(mesh, labels, highlight=None) -> trimesh.Trimesh:
    """Color the mesh by label.

    Args:
        mesh (trimesh.Trimesh): The mesh to color.
        labels (np.ndarray): The labels for each vertex.
        highlight (int, optional): array of vertex indices to highlight in red. Defaults to None.

    Returns:
        trimesh.Trimesh: The colored mesh.
    """
    label_idx = np.searchsorted(ALL_CODES, labels) #position of each label in ALL_CODES
    assert np.array_equal(ALL_CODES[label_idx], labels), "labels must be a valid code" # ensure every label is valid code
    
    cmap = matplotlib.colormaps["tab20"]
    palette = cmap(np.arange(len(ALL_CODES))%20) #get colors for each label
    palette[0] = [0.5, 0.5, 0.5, 1] #set color for label 0 to gray
    vertex_colors = palette[label_idx]
    if highlight is not None:
        vertex_colors[highlight] = [1, 0, 0, 1] #highlight vertex in red
    colored_mesh = mesh.copy()
    vertex_colors = (vertex_colors * 255).round().astype(np.uint8) #convert to uint8 for trimesh
    colored_mesh.visual.vertex_colors = vertex_colors
    return colored_mesh

if __name__ == "__main__":
    import argparse
    from load_scan import load_scan
    parser = argparse.ArgumentParser(description="Color a mesh by label.")
    parser.add_argument("scan_path", type=str, help="Path to the scan directory.")
    parser.add_argument("--out", type=str, help="Path to save the colored mesh.", default="results/colored_mesh.ply")
    parser.add_argument("--highlight", type=int, nargs="+", help="Vertex indices to highlight in red.", default=None)
    args = parser.parse_args()
    data = load_scan(args.scan_path)
    colored_mesh = color_by_label(data.mesh, data.labels, highlight=args.highlight)
    colored_mesh.export(args.out)
    #colored_mesh.show()