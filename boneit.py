import bpy

bl_info = {
    "name": "Bone It!",
    "author": "ZuneDai",
    "version": (0,0, 3),
    "location": "View 3D > Object Mode > Tool Shelf",
    "blender": (3, 5, 0),
    "description": "This is an addon to very quickly set up a complex rig for bones based on Pierrick Picaut's advanced tentacle rig. For now, this addon only supports the rigging of tail or tentacle rigs. To use, create 1 bone, select the bone in the middle, type in your armature name and select how many bones you want. then click bone it and tweak it.",
    "warning": "",
    "category": "Rigging",
    }

class VIEW3D_PT_bone_rig_adv(bpy.types.Panel):
    bl_label = "Tenta_rig"
    bl_idname = "VIEW3D_PT_bone_rig_adv"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone It!'

    def draw(self, context):
        layout = self.layout

        # Number of Bones field
        row = layout.row()
        row.prop(context.scene, "num_bones", text="Number of Bones")

        # Bone Name field
        row = layout.row()
        row.prop(context.scene, "bone_name", text="Bone Name")

        # Bone It button
        row = layout.row()
        row.operator("object.bone_it", text="Bone It")

        # Create Tweaker button
        row = layout.row()
        row.operator("object.tweak_it", text="Tweak It")
        
class OBJECT_OT_bone_it(bpy.types.Operator):
    bl_idname = "object.bone_it"
    bl_label = "Bone It"

    def execute(self, context):
        num_bones = context.scene.num_bones
        bone_name = context.scene.bone_name

        # Subdivide selected bone
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.subdivide(number_cuts=num_bones-1)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Rename bones
        obj = context.active_object
        bones = obj.data.bones

        bone_index = 0
        for bone in bones:
            bone.name = bone_name + "_BI_" + chr(ord('a') + bone_index)
            bone_index += 1
            
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.name = bone_name

        return {'FINISHED'}
    
class OBJECT_OT_tweak_it(bpy.types.Operator):
    bl_idname = "object.tweak_it"
    bl_label = "Bone It"

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        num_bones = context.scene.num_bones
        bone_name = context.scene.bone_name

        # Select the end bone, extrude it and rename it
        bpy.ops.object.select_pattern(pattern="*_BI_" + chr(ord('a') + (num_bones-1)),extend=False)
        bpy.ops.armature.select_less()
        bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.1), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bpy.ops.object.select_pattern(pattern=bone_name + "_BI_" + chr(ord('a') + (num_bones-1)) + ".001",extend=False)
        bpy.context.active_bone.name = bone_name + "_BT_" + "TWEAKER_TIP" 
        bpy.ops.armature.parent_clear(type='CLEAR')
        
        # Select the other bones and clear parenting
        bpy.ops.object.select_pattern(pattern=bone_name + "*_BI_*",extend=False)
        bpy.ops.armature.parent_clear(type='CLEAR')
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.object.select_pattern(pattern="*_BI_*",extend=False)
        bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate=None, TRANSFORM_OT_translate=None)
        bpy.ops.transform.resize(value=(0.3, 0.3, 0.3), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
       
        # Rename tweaker bones
        select = bpy.ops.object.select_pattern
        for bone in bpy.context.selected_bones:
          if ".001" in bone.name:
            new_name = bone.name.replace(".001", "_TWEAKER")
            bone.name = new_name
        
        #############
        ## Parent and stretch bones ##
        
        # switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # get all the bones in the armature
        obj = bpy.context.active_object
        arm = obj.data
        bone_names = [bone.name for bone in arm.edit_bones]

        # loop through all the bones and parent the ones without TWEAKER to the ones with TWEAKER
        for i in range(len(bone_names)):
            bone_name = bone_names[i]
            if "_TWEAKER" not in bone_name:
                parent_name = bone_name + "_TWEAKER"
                if parent_name in bone_names:
                    arm.edit_bones[bone_name].parent = arm.edit_bones[parent_name]

        # switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
                ###############
        
        # Set up stretch-to constraints for each bone        
        bone_suffixes = [chr(i) for i in range(ord('a'), ord('a') + num_bones)]
        bone_name = context.scene.bone_name
        armature = bpy.context.active_object

        bpy.ops.object.mode_set(mode='POSE')
        for i, suffix in enumerate(bone_suffixes):
            bone_name_bi_suffix = f"{bone_name}_BI_{suffix}"
            bone_name_bi_suffix_tweaker = f"{bone_name}_BI_{bone_suffixes[i+1]}_TWEAKER" if i < num_bones-1 else f"{bone_name}_BT_TWEAKER_TIP"

            bone_bi = armature.pose.bones[bone_name_bi_suffix]
            bone_tweaker = armature.pose.bones[bone_name_bi_suffix_tweaker]
            stretch_to = bone_bi.constraints.new(type='STRETCH_TO')
            stretch_to.target = armature
            stretch_to.subtarget = bone_tweaker.name
    

        ###

        return {'FINISHED'}

def register():
    bpy.types.Scene.num_bones = bpy.props.IntProperty(
        name="Number of Bones",
        description="Number of bones to create",
        default=3,
        min=2,
        max=26
    )

    bpy.types.Scene.bone_name = bpy.props.StringProperty(
        name="Bone Name",
        description="Base name of the bones to create",
        default="bone"
    )

    bpy.utils.register_class(VIEW3D_PT_bone_rig_adv)
    bpy.utils.register_class(OBJECT_OT_bone_it)
    bpy.utils.register_class(OBJECT_OT_tweak_it)
    bpy.types.Scene.num_bones = bpy.props.IntProperty(name="Number of Bones", default=3)
    bpy.types.Scene.bone_name = bpy.props.StringProperty(name="Bone Name", default="bone")

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_bone_rig_adv)
    bpy.utils.unregister_class(OBJECT_OT_bone_it)
    bpy.utils.unregister_class(OBJECT_OT_tweak_it)
    del bpy.types.Scene.num_bones
    del bpy.types.Scene.bone_name

if __name__ == "__main__":
    register()