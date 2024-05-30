import bpy
import bmesh

# Define the colors for each face of the Rubik's Cube
face_colors = {
    "Top": (1, 1, 1, 1),  # White
    "Bottom": (1, 1, 0, 1),  # Yellow
    "Front": (0, 1, 0, 1),  # Green
    "Back": (0, 0, 1, 1),  # Blue
    "Right": (1, 0.5, 0, 1),  # Orange
    "Left": (1, 0, 0, 1),  # Red
    "Internal": (0, 0, 0, 1),  # Black for internal faces
    "Bevel": (0, 0, 0, 1),  # Black for bevels
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
                0.5  # Roughness for a plastic effect
            )
        if "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.5  # Specular for a shiny effect

    material_cache[color_name] = material
    return material


# Assign color to a face
def assign_material_to_face(obj, face, color):
    mat = get_or_create_material(color, face_colors[color])
    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    face.material_index = obj.data.materials.find(mat.name)


# Manually create and color the bevels
def create_and_color_bevels(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bevel(offset=0.15, segments=30)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Assign black material to bevels
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.edges_select_sharp(sharpness=0.5)
    bpy.ops.object.material_slot_add()
    obj.material_slots[-1].material = get_or_create_material(
        "Bevel", face_colors["Bevel"]
    )
    bpy.ops.object.material_slot_assign()
    bpy.ops.object.mode_set(mode="OBJECT")


# Create a mini-cube with colored faces and manual bevels
def create_minicube(x, y, z, size, rubiks_cube_size):
    # Create the minicube mesh
    mesh = bpy.data.meshes.new(name="MinicubeMesh")
    minicube = bpy.data.objects.new(name="Minicube", object_data=mesh)
    bpy.context.collection.objects.link(minicube)

    # Create the minicube geometry
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh)
    bm.free()

    # Switch to edit mode to manipulate faces
    bpy.context.view_layer.objects.active = minicube
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(mesh)

    # Assign materials to the faces based on position
    for face in bm.faces:
        normal = face.normal
        if normal.z > 0.5 and z == rubiks_cube_size - 1:
            assign_material_to_face(minicube, face, "Top")
        elif normal.z < -0.5 and z == 0:
            assign_material_to_face(minicube, face, "Bottom")
        elif normal.y > 0.5 and y == rubiks_cube_size - 1:
            assign_material_to_face(minicube, face, "Front")
        elif normal.y < -0.5 and y == 0:
            assign_material_to_face(minicube, face, "Back")
        elif normal.x > 0.5 and x == rubiks_cube_size - 1:
            assign_material_to_face(minicube, face, "Right")
        elif normal.x < -0.5 and x == 0:
            assign_material_to_face(minicube, face, "Left")
        else:
            assign_material_to_face(
                minicube, face, "Internal"
            )  # Internal faces are black

    # Return to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Manually create and color the bevels
    create_and_color_bevels(minicube)

    # Set location
    minicube.location = (x * size, y * size, z * size)

    return minicube


def create_rubiks_cube(size):
    # Create the parent empty object directly
    parent = bpy.data.objects.new("RubiksCube", None)
    bpy.context.collection.objects.link(parent)

    cube_size = 2  # Adjust the size of the mini-cubes to avoid gaps
    i = 1
    for x in range(size):
        for y in range(size):
            for z in range(size):
                minicube = create_minicube(x, y, z, cube_size, size)
                minicube.name = "Minicube " + str(i)
                i += 1
                minicube.parent = (
                    parent  # Set the parent of the minicube to the RubiksCube
                )
