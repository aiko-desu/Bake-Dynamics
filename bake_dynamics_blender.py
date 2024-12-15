bl_info = {
    "name": "Bake Simulation Nodes and Dynamics",
    "blender": (4, 1, 0),
    "category": "Bake",
    "version": (1, 1),
    "location": "View3D > N-Panel > Bake",
    "author": "Aiko",
    "description": "Bakes simulation, dynamics for current scene Range.",
}

import bpy
import os

# Define the base directory for baking
def get_bake_directory(context):
    name = bpy.path.basename(bpy.context.blend_data.filepath)[:-6]
    #return bpy.path.abspath("//bake/" + name)
    return "//baked_cache/" + name

# Enable disk caching for all particle systems
def enable_disk_cache():
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'PARTICLE_SYSTEM':
                    particle_system = modifier.particle_system
                    if particle_system:
                        # Enable disk cache
                        particle_system.point_cache.use_disk_cache = True
# Enable disk caching for all particle systems
def disable_disk_cache():
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'PARTICLE_SYSTEM':
                    particle_system = modifier.particle_system
                    if particle_system:
                        # Disable disk cache
                        particle_system.point_cache.use_disk_cache = False

class BakeSimulationNodesOperator(bpy.types.Operator):
    bl_idname = "object.bake_simulation_nodes"
    bl_label = "Bake Simulation Nodes"
    bl_description = "Bake simulation nodes for all mesh objects in the current view layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        wahoo = os.path.join(get_bake_directory(context), "simulation_nodes")
        
        # Set the simulation frame range to match the animation frame range
        bpy.context.scene.simulation_frame_start = bpy.context.scene.frame_start
        bpy.context.scene.simulation_frame_end = bpy.context.scene.frame_end
        
        # Deselect all objects in the current view layer
        bpy.ops.object.select_all(action='DESELECT')
        
        # Track if any objects are selected and have simulation nodes
        selected_with_sim_nodes = False
        
        # Iterate through all objects in the current view layer
        for obj in bpy.context.view_layer.objects:
            if obj.type == 'MESH':
                if obj.modifiers:
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES':
                            # Set the bake directory
                            modifier.bake_directory = wahoo
                            obj.select_set(True)
                            obj.use_simulation_cache = True
                            selected_with_sim_nodes = True
        
        # Only bake if there are selected objects with simulation nodes
        if selected_with_sim_nodes:
            bpy.ops.object.simulation_nodes_cache_delete(selected=True)
            bpy.ops.object.simulation_nodes_cache_bake(selected=True)
        else:
            self.report({'INFO'}, "No objects have simulation nodes. Skipping bake operation.")
                            
        return {'FINISHED'}

class DisablePlaybackCachingOperator(bpy.types.Operator):
    bl_idname = "object.disable_playback_caching"
    bl_label = "Disable"
    bl_description = "Disable Playback Caching for Simulation Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        # Uncheck Cache
        for obj in bpy.context.view_layer.objects:
            if obj.type == 'MESH':
                if obj.modifiers:
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES':
                            obj.use_simulation_cache = False
        
        self.report({'INFO'}, "Disabled Playback Caching for Simulation Nodes")                    
        return {'FINISHED'}
    
class EnablePlaybackCachingOperator(bpy.types.Operator):
    bl_idname = "object.enable_playback_caching"
    bl_label = "Enable"
    bl_description = "Enable Playback Caching for Simulation Nodes(Use after Bake)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        # Uncheck Cache
        for obj in bpy.context.view_layer.objects:
            if obj.type == 'MESH':
                if obj.modifiers:
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES':
                            obj.use_simulation_cache = True
        
        self.report({'INFO'}, "Enable Playback Caching for Simulation Nodes")                    
        return {'FINISHED'}
    

# Operator to bake all dynamics
class BakeAllDynamicsOperator(bpy.types.Operator):
    bl_idname = "object.bake_all_dynamics"
    bl_label = "Bake All Dynamics"
    bl_description = "Bake all dynamics including particle systems, cloth, soft bodies, etc."
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bake_directory = get_bake_directory(context)
        
        # Disable  disk caching and set the cache path for particle systems
        enable_disk_cache()

        # Bake all dynamics (including particle systems, cloth, soft bodies, etc.)
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        return {'FINISHED'}

# Operator to bake all simulation and dynamics
class BakeAllOperator(bpy.types.Operator):
    bl_idname = "object.bake_all_simulation_and_dynamics"
    bl_label = "Bake All"
    bl_description = "Bake all simulation nodes and dynamics in the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.bake_all_dynamics()
        # Bake simulation nodes first
        bpy.ops.object.bake_simulation_nodes()
        # Then bake all dynamics

        
        return {'FINISHED'}

# Operator to bake all simulation and dynamics and start rendering
class BakeAllAndRenderOperator(bpy.types.Operator):
    bl_idname = "object.bake_all_and_render"
    bl_label = "Bake All and Render"
    bl_description = "Bake all simulation nodes and dynamics and start rendering the animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        # Bake all dynamics
        bpy.ops.object.bake_all_dynamics()
        
        # Bake simulation nodes
        bpy.ops.object.bake_simulation_nodes()
        
        # Start rendering the animation
        #bpy.ops.render.render(animation=True)
        override = {
            'scene': bpy.context.scene,
        }
        bpy.ops.render.render(override, 'INVOKE_DEFAULT', animation=True)
        
        return {'FINISHED'}

# Panel to add buttons in the UI
class BakeSimulationNodesPanel(bpy.types.Panel):
    bl_label = "Bake"
    bl_idname = "OBJECT_PT_bake_simulation_nodes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bake'
    
    def draw(self, context):
        layout = self.layout
        
        #box = layout.box()
        #box.label(text="low IQ? Click n sleep", icon='RENDER_ANIMATION')
        # Add the larger button inside the box
        #row = box.row()
        #row.scale_y = 3  # Increase the vertical size of the button
        #row.operator("object.bake_all_and_render", text="Bake All and Start Render")
        
        
        # Add buttons with a more prominent last button
        row = layout.row()
        row.scale_y = 2
        row.operator("object.bake_all_simulation_and_dynamics")
        layout.operator("object.bake_simulation_nodes")
        layout.operator("object.bake_all_dynamics")
        
        #playback caching
        box = layout.box()        
        box.label(text=" Playback Caching")
        row = box.row()
        row.operator("object.disable_playback_caching")
        row.operator("object.enable_playback_caching")
        

def register():
    bpy.utils.register_class(BakeSimulationNodesOperator)
    bpy.utils.register_class(BakeAllDynamicsOperator)
    bpy.utils.register_class(BakeAllOperator)
    bpy.utils.register_class(BakeAllAndRenderOperator)
    bpy.utils.register_class(BakeSimulationNodesPanel)
    bpy.utils.register_class(DisablePlaybackCachingOperator)
    bpy.utils.register_class(EnablePlaybackCachingOperator)

def unregister():
    bpy.utils.unregister_class(BakeSimulationNodesOperator)
    bpy.utils.unregister_class(BakeAllDynamicsOperator)
    bpy.utils.unregister_class(BakeAllOperator)
    bpy.utils.unregister_class(BakeAllAndRenderOperator)
    bpy.utils.unregister_class(BakeSimulationNodesPanel)
    bpy.utils.register_class(DisablePlaybackCachingOperator)
    bpy.utils.register_class(EnablePlaybackCachingOperator)

if __name__ == "__main__":
    register()