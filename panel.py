import bpy


# Create the Rubiks Cube object on the right sidebar Panel (Shortcut: n)
class RubiksCubePanel(bpy.types.Panel):
    bl_label = "Rubik's Cube"
    bl_idname = "OBJECT_PT_rubikscube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RubiksCube Generator"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "rubiks_cube_size")
        layout.operator("mesh.add_rubikscube")


def register():
    bpy.utils.register_class(RubiksCubePanel)
    bpy.types.Scene.rubiks_cube_size = bpy.props.IntProperty(
        name="Size", default=4, min=3, max=50
    )


def unregister():
    bpy.utils.unregister_class(RubiksCubePanel)
    del bpy.types.Scene.rubiks_cube_size
