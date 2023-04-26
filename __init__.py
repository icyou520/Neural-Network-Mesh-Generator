import bpy
import mathutils

# Add-on information
bl_info = {
    "name": "Neural Network 3D Visualization",
    "author": "Deep Belief",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Neural Network",
    "description": "Generate a 3D visualization of a neural network",
    "category": "Add Mesh",
}

class NeuralNetworkProperties(bpy.types.PropertyGroup):
    num_layers: bpy.props.IntProperty(name="Num Layers", default=5, min=1, max=10)
    nodes_per_layer: bpy.props.IntProperty(name="Nodes per Layer", default=5, min=1, max=10)
    depth_layers: bpy.props.IntProperty(name="Depth Layers", default=2, min=1, max=5)
    layer_spacing: bpy.props.FloatProperty(name="Layer Spacing", default=2, min=0.1, max=10)
    node_spacing: bpy.props.FloatProperty(name="Node Spacing", default=1, min=0.1, max=10)
    depth_spacing: bpy.props.FloatProperty(name="Depth Spacing", default=2, min=0.1, max=10)
    sphere_radius: bpy.props.FloatProperty(name="Sphere Radius", default=0.1, min=0.01, max=1)
    cylinder_radius: bpy.props.FloatProperty(name="Cylinder Radius", default=0.05, min=0.01, max=1)

class NeuralNetworkGenerateOperator(bpy.types.Operator):
    bl_idname = "neural_network.generate"
    bl_label = "Generate Neural Network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.neural_network_props
        create_neural_network_visualization(props)
        return {'FINISHED'}

def create_neural_network_visualization(props):
    num_layers = props.num_layers
    nodes_per_layer = props.nodes_per_layer
    depth_layers = props.depth_layers
    layer_spacing = props.layer_spacing
    node_spacing = props.node_spacing
    depth_spacing = props.depth_spacing
    sphere_radius = props.sphere_radius
    cylinder_radius = props.cylinder_radius

    def create_sphere(location):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=sphere_radius, location=location)
        sphere = bpy.context.active_object
        return sphere

    def create_cylinder_between_points(p1, p2):
        vec = p2 - p1
        dist = vec.length
        vec.normalize()

        bpy.ops.mesh.primitive_cylinder_add(radius=cylinder_radius, depth=dist, location=p1 + vec * dist / 2)
        cylinder = bpy.context.active_object
        dir_vec = mathutils.Vector((0, 0, 1))
        quat = dir_vec.rotation_difference(vec)
        cylinder.rotation_mode = 'QUATERNION'
        cylinder.rotation_quaternion = quat
        return cylinder

    for d in range(depth_layers):
        for i in range(num_layers):
            for j in range(nodes_per_layer):
                pos = mathutils.Vector((d * depth_spacing + i * layer_spacing, j * node_spacing, d * depth_spacing))
                sphere = create_sphere(pos)

                if i > 0:
                    prev_layer_start = (i - 1) * nodes_per_layer
                    for k in range(nodes_per_layer):
                        prev_node = prev_layer_start + k + d * num_layers
                        prev_pos = mathutils.Vector((d * depth_spacing + (i - 1) * layer_spacing, k * node_spacing, d * depth_spacing))
                        create_cylinder_between_points(pos, prev_pos)

                if d > 0:
                    prev_depth_start = ((d - 1) * num_layers * nodes_per_layer) + (i * nodes_per_layer)
                    prev_depth_node = prev_depth_start + j
                    prev_depth_pos = mathutils.Vector(((d - 1) * depth_spacing + i * layer_spacing, j * node_spacing, (d - 1) * depth_spacing))
                    create_cylinder_between_points(pos, prev_depth_pos)

                    if i > 0:
                        for k in range(nodes_per_layer):
                            prev_node = prev_depth_start + (i - 1) * nodes_per_layer + k
                            prev_node_pos = mathutils.Vector(((d - 1) * depth_spacing + (i - 1) * layer_spacing, k * node_spacing, (d - 1) * depth_spacing))
                            create_cylinder_between_points(pos, prev_node_pos)

class NeuralNetworkPanel(bpy.types.Panel):
    bl_label = "Neural Network"
    bl_idname = "OBJECT_PT_neural_network"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Neural Network'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.neural_network_props

        layout.prop(props, "num_layers")
        layout.prop(props, "nodes_per_layer")
        layout.prop(props, "depth_layers")
        layout.prop(props, "layer_spacing")
        layout.prop(props, "node_spacing")
        layout.prop(props, "depth_spacing")
        layout.prop(props, "sphere_radius")
        layout.prop(props, "cylinder_radius")

        layout.operator("neural_network.generate")

classes = (NeuralNetworkProperties, NeuralNetworkGenerateOperator, NeuralNetworkPanel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.neural_network_props = bpy.props.PointerProperty(type=NeuralNetworkProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.neural_network_props

if __name__ == "__main__":
    register()
