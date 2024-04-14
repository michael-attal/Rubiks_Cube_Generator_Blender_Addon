import bpy
from bpy.types import Operator
from . import rubiks_cube


# Display the Add RubiksCube button inside the right sidebar panel and create RubiksCube on click
class RubiksCubeOperator(Operator):
    bl_idname = "mesh.add_rubikscube"
    bl_label = "Add RubiksCube"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        rubiks_cube.create_rubiks_cube(context.scene.rubiks_cube_size)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(RubiksCubeOperator)


def unregister():
    bpy.utils.unregister_class(RubiksCubeOperator)
