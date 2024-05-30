import bpy
import bmesh
import time

# Define the colors for each face of the Rubik's Cube
face_colors = {
    "White": (1, 1, 1, 1),
    "Yellow": (1, 1, 0, 1),
    "Green": (0, 1, 0, 1),
    "Blue": (0, 0, 1, 1),
    "Orange": (1, 0.5, 0, 1),
    "Red": (1, 0, 0, 1),
    "Default": (0, 0, 0, 1),  # Black for default cube color
}

# Cache for materials to avoid recreating them
material_cache = {}


# Create or get a material by color name
def get_or_create_material(color_name, color_value):
    if color_name in material_cache:
        return material_cache[color_name]
    if color_name in bpy.data.materials:
        material = bpy.data.materials[color_name]
    else:
        material = bpy.data.materials.new(name=color_name)
        material.use_nodes = True  # Enable nodes for more realistic materials

        # Ensure the Principled BSDF node exists
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            bsdf = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")

        # Set the base color
        bsdf.inputs["Base Color"].default_value = color_value

        # Set roughness and specular values if they exist
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = (
                0.5  # Adjust roughness for a plastic effect
            )
        if "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = (
                0.5  # Adjust specular for a shiny effect
            )

    material_cache[color_name] = material
    return material


# Create a single colored face (tile) for a mini-cube
def create_tile(color, size, location, rotation, minicube, face_name):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0), rotation=rotation)
    tile = bpy.context.active_object
    tile.name = f"{minicube.name} {face_name} Tile"
    mat = get_or_create_material(color, face_colors[color])
    if len(tile.data.materials):
        tile.data.materials[0] = mat
    else:
        tile.data.materials.append(mat)
    tile.parent = minicube  # Setting the parent to the minicube
    tile.location = location  # Correct the location relative to the parent
    return tile


# Create a mini-cube with colored tiles and a bevel modifier using BMesh
def create_minicube(x, y, z, size, rubiks_cube_size):
    mesh = bpy.data.meshes.new(name="MinicubeMesh")
    minicube = bpy.data.objects.new(name="Minicube", object_data=mesh)
    bpy.context.collection.objects.link(minicube)

    # Create the minicube geometry using BMesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh)
    bm.free()

    # Assign the default black material to the entire mini-cube
    mat_default = get_or_create_material("Default", face_colors["Default"])
    if len(mesh.materials):
        mesh.materials[0] = mat_default
    else:
        mesh.materials.append(mat_default)

    # Add a Bevel modifier to the minicube
    bevel = minicube.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.2  # Reduce width for better performance
    bevel.segments = 2  # Further reduced segments for performance

    # Apply the Bevel modifier in object mode
    bpy.context.view_layer.objects.active = minicube
    bpy.ops.object.modifier_apply(modifier="Bevel")

    # Add tiles to each face of the mini-cube
    tile_size = size * 0.8
    tile_offset = size * 0.505  # Slightly greater than half to avoid z-fighting

    # Use a dictionary to store rotations for each face
    rotations = {
        "Top": (0, 0, 0),
        "Bottom": (0, 0, 0),
        "Front": (1.5708, 0, 0),
        "Back": (1.5708, 0, 0),
        "Right": (0, 1.5708, 0),
        "Left": (0, 1.5708, 0),
    }

    # Create tiles only for the exposed faces
    for face in minicube.data.polygons:
        normal = face.normal
        if normal.z > 0.5 and z == rubiks_cube_size - 1:
            create_tile(
                "White",
                tile_size,
                (0, 0, tile_offset),
                rotations["Top"],
                minicube,
                "Top",
            )
        elif normal.z < -0.5 and z == 0:
            create_tile(
                "Yellow",
                tile_size,
                (0, 0, -tile_offset),
                rotations["Bottom"],
                minicube,
                "Bottom",
            )
        elif normal.y > 0.5 and y == rubiks_cube_size - 1:
            create_tile(
                "Green",
                tile_size,
                (0, tile_offset, 0),
                rotations["Front"],
                minicube,
                "Front",
            )
        elif normal.y < -0.5 and y == 0:
            create_tile(
                "Blue",
                tile_size,
                (0, -tile_offset, 0),
                rotations["Back"],
                minicube,
                "Back",
            )
        elif normal.x > 0.5 and x == rubiks_cube_size - 1:
            create_tile(
                "Orange",
                tile_size,
                (tile_offset, 0, 0),
                rotations["Right"],
                minicube,
                "Right",
            )
        elif normal.x < -0.5 and x == 0:
            create_tile(
                "Red",
                tile_size,
                (-tile_offset, 0, 0),
                rotations["Left"],
                minicube,
                "Left",
            )

    # Set location
    minicube.location = (x * size, y * size, z * size)

    return minicube


def create_rubiks_cube(size):
    start_time = time.time()
    # Create the parent empty object directly
    parent = bpy.data.objects.new("RubiksCube", None)
    bpy.context.collection.objects.link(parent)

    cube_size = 2  # Adjust the size of the mini-cubes to avoid gaps
    i = 1
    for x in range(size):
        for y in range(size):
            for z in range(size):
                # Skip the inner cubes as they are not visible
                if x in [1, size - 2] and y in [1, size - 2] and z in [1, size - 2]:
                    continue
                print(f"Creating minicube {i} at ({x}, {y}, {z})")
                minicube = create_minicube(x, y, z, cube_size, size)
                minicube.name = "Minicube " + str(i)
                i += 1
                minicube.parent = (
                    parent  # Set the parent of the minicube to the RubiksCube
                )

    end_time = time.time()
    print(f"Rubik's Cube creation completed in {end_time - start_time} seconds")
