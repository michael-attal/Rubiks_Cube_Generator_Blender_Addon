import bpy

# Define the colors for each face of the Rubik's Cube
face_colors = {
    "White": (1, 1, 1, 1),
    "Yellow": (1, 1, 0, 1),
    "Green": (0, 1, 0, 1),
    "Blue": (0, 0, 1, 1),
    "Orange": (1, 0.5, 0, 1),
    "Red": (1, 0, 0, 1),
}


# Create or get a material by color name
def get_or_create_material(color_name):
    if color_name in bpy.data.materials:
        return bpy.data.materials[color_name]
    else:
        mat = bpy.data.materials.new(name=color_name)
        mat.diffuse_color = face_colors[color_name]
        mat.use_nodes = False
        return mat


# Create a single colored face (tile) for a mini-cube
def create_tile(color, size, location, rotation, minicube, face_name):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0), rotation=rotation)
    tile = bpy.context.active_object
    tile.name = f"{minicube.name} {face_name} Tile"
    mat = get_or_create_material(color)
    if len(tile.data.materials):
        tile.data.materials[0] = mat
    else:
        tile.data.materials.append(mat)
    tile.parent = minicube  # Setting the parent to the minicube
    tile.location = location  # Correct the location relative to the parent
    return tile


# Create a mini-cube with colored tiles
def create_minicube(x, y, z, size):
    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z))
    minicube = bpy.context.active_object

    # Add colored tiles to each face of the mini-cube
    tile_size = size * 0.9
    tile_offset = size * 0.505  # Slightly greater than half to avoid z-fighting
    create_tile(
        "White", tile_size, (0, 0, tile_offset), (0, 0, 0), minicube, "Top"
    )  # Top face
    create_tile(
        "Yellow", tile_size, (0, 0, -tile_offset), (0, 0, 0), minicube, "Bottom"
    )  # Bottom face
    create_tile(
        "Green", tile_size, (0, tile_offset, 0), (1.5708, 0, 0), minicube, "Front"
    )  # Front face
    create_tile(
        "Blue", tile_size, (0, -tile_offset, 0), (1.5708, 0, 0), minicube, "Back"
    )  # Back face
    create_tile(
        "Orange", tile_size, (tile_offset, 0, 0), (0, 1.5708, 0), minicube, "Right"
    )  # Right face
    create_tile(
        "Red", tile_size, (-tile_offset, 0, 0), (0, 1.5708, 0), minicube, "Left"
    )  # Left face

    return minicube


def create_rubiks_cube(size):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    parent = bpy.context.active_object
    parent.name = "RubiksCube"

    cube_size = 2.1  # Adjust the size of the mini-cubes to avoid gaps
    i = 1
    for x in range(size):
        for y in range(size):
            for z in range(size):
                # Skip the inner cubes as they are not visible
                if x in [1, size - 2] and y in [1, size - 2] and z in [1, size - 2]:
                    continue
                minicube = create_minicube(
                    (x - size // 2) * cube_size,
                    (y - size // 2) * cube_size,
                    (z - size // 2) * cube_size,
                    cube_size,
                )
                minicube.name = "Minicube " + str(i)
                i += 1
                minicube.parent = (
                    parent  # Set the parent of the minicube to the RubiksCube
                )
