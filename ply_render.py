import bpy
from bpy import context
from bpy.props import StringProperty

bl_info = {
    "name": "PLY Render",
    "blender": (3, 0, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "Sp1der",
    "description": "Process PLY objects with shading and geometry nodes"
}


def create_ply_material(name="PLY_Material", use_emission=False, emission_strength=0.02):
    """创建PLY材质并使用Col属性作为颜色输入"""
    # 每次重建材质以反映最新设置
    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat)
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # 清除默认节点
    mat.node_tree.nodes.clear()
    
    # 创建节点
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 创建输出节点
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 300)
    
    # 创建Principled BSDF
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 300)
    
    # 创建属性节点用于获取Col属性
    attr_node = nodes.new(type='ShaderNodeAttribute')
    attr_node.attribute_name = 'Col'
    attr_node.location = (0, 300)
    
    # 连接节点：Col属性 -> 基础颜色 -> 输出
    links.new(attr_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # 自发光设置（兼容 Blender 3.x / 4.x）
    emission_color_input = (bsdf_node.inputs.get('Emission Color')
                            or bsdf_node.inputs.get('Emission'))
    if use_emission and emission_color_input:
        links.new(attr_node.outputs['Color'], emission_color_input)
        if 'Emission Strength' in bsdf_node.inputs:
            bsdf_node.inputs['Emission Strength'].default_value = emission_strength
    else:
        if 'Emission Strength' in bsdf_node.inputs:
            bsdf_node.inputs['Emission Strength'].default_value = 0.0
    
    return mat


def apply_geometry_nodes(obj, material, radius=0.01):
    """应用几何节点：mesh转为点，设置半径和材质"""
    
    # 创建或获取几何节点修改器
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES':
            modifier = mod
            break
    
    if not modifier:
        modifier = obj.modifiers.new(name="PLY_GeometryNodes", type='NODES')
    
    # 创建新的节点树
    node_tree_name = f"{obj.name}_GeoNodes"
    node_tree = bpy.data.node_groups.new(name=node_tree_name, type='GeometryNodeTree')
    modifier.node_group = node_tree

    # 声明节点组的 Geometry 接口（Blender 4.0+ 与 3.x 兼容）
    if hasattr(node_tree, 'interface'):
        # Blender 4.0+
        node_tree.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        node_tree.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        # Blender 3.x
        node_tree.inputs.new('NodeSocketGeometry', 'Geometry')
        node_tree.outputs.new('NodeSocketGeometry', 'Geometry')

    nodes = node_tree.nodes
    links = node_tree.links
    
    # 清除默认节点
    nodes.clear()
    
    # 创建输入输出节点
    input_node = nodes.new(type='NodeGroupInput')
    input_node.location = (0, 0)
    
    output_node = nodes.new(type='NodeGroupOutput')
    output_node.location = (600, 0)
    
    # 创建Mesh to Points节点
    mesh_to_points = nodes.new(type='GeometryNodeMeshToPoints')
    mesh_to_points.location = (150, 0)
    mesh_to_points.inputs['Radius'].default_value = radius
    
    # 创建Set Material节点
    set_material = nodes.new(type='GeometryNodeSetMaterial')
    set_material.location = (350, 0)
    set_material.inputs['Material'].default_value = material
    
    # 用索引 0 连接 Group Input/Output，避免 key 找不到的问题
    links.new(input_node.outputs[0], mesh_to_points.inputs['Mesh'])
    links.new(mesh_to_points.outputs['Points'], set_material.inputs['Geometry'])
    links.new(set_material.outputs['Geometry'], output_node.inputs[0])


class PLY_OT_ProcessObject(bpy.types.Operator):
    """处理PLY对象：应用着色节点和几何节点"""
    bl_idname = "object.ply_process"
    bl_label = "Process PLY Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """检查是否选中了对象"""
        return context.active_object is not None
    
    def execute(self, context):
        try:
            obj = context.active_object
            scene = context.scene
            
            # 1. 创建PLY材质（着色节点设置）
            mat_name = f"{obj.name}_PLY_Material"
            material = create_ply_material(
                name=mat_name,
                use_emission=scene.ply_use_emission,
                emission_strength=scene.ply_emission_strength
            )
            
            # 如果对象还没有赋予材质，添加材质槽
            if not obj.data.materials:
                obj.data.materials.append(material)
            else:
                obj.data.materials[0] = material
            
            # 2. 应用几何节点
            apply_geometry_nodes(obj, material, radius=scene.ply_radius)
            
            self.report({'INFO'}, f"✓ PLY对象 '{obj.name}' 处理完成")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"处理失败: {str(e)}")
            return {'CANCELLED'}


class PLY_PT_RenderPanel(bpy.types.Panel):
    """PLY渲染工具面板"""
    bl_label = "PLY Render Tools"
    bl_idname = "PLY_PT_render_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box = layout.box()
        box.label(text="PLY 对象处理", icon='CUBE')
        
        # 点半径输入
        box.prop(scene, "ply_radius", text="点半径 (Radius)")
        
        # 自发光设置
        row = box.row()
        row.prop(scene, "ply_use_emission", text="启用自发光")
        sub = box.row()
        sub.enabled = scene.ply_use_emission
        sub.prop(scene, "ply_emission_strength", text="自发光强度")
        
        row = box.row()
        row.operator("object.ply_process",
                    text="处理PLY对象",
                    icon='MATERIAL')
        
        box.label(text="操作结果:")
        if context.active_object:
            obj = context.active_object
            box.label(text=f"选中对象: {obj.name}", icon='OBJECT_DATA')
            
            # 显示是否已应用几何节点
            has_geo_nodes = any(mod.type == 'NODES' for mod in obj.modifiers)
            icon = 'FILE_TICK' if has_geo_nodes else 'MESH_DATA'
            box.label(text=f"几何节点: {'已应用' if has_geo_nodes else '未应用'}", icon=icon)


def register():
    """注册插件类"""
    bpy.utils.register_class(PLY_OT_ProcessObject)
    bpy.utils.register_class(PLY_PT_RenderPanel)
    bpy.types.Scene.ply_radius = bpy.props.FloatProperty(
        name="点半径",
        default=0.01,
        min=0.0001,
        soft_max=1.0,
        precision=4
    )
    bpy.types.Scene.ply_use_emission = bpy.props.BoolProperty(
        name="启用自发光",
        default=False
    )
    bpy.types.Scene.ply_emission_strength = bpy.props.FloatProperty(
        name="自发光强度",
        default=0.6,
        min=0.0,
        soft_max=10.0,
        precision=3
    )


def unregister():
    """取消注册插件类"""
    bpy.utils.unregister_class(PLY_OT_ProcessObject)
    bpy.utils.unregister_class(PLY_PT_RenderPanel)
    del bpy.types.Scene.ply_radius
    del bpy.types.Scene.ply_use_emission
    del bpy.types.Scene.ply_emission_strength


if __name__ == "__main__":
    register()
    print("PLY Render 插件已加载")
