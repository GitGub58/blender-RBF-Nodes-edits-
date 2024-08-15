"""
Functions and classes for RBF Operators "Add Multiple"->"Objects Input Nodes (Selected)" ( node.add_nodes_input_from_selected) and "Objects Output Nodes (Selected)" (node.add_nodes_output_from_selected).

These operators create multiple connected Input/Output Nodes from selected Objects or Bones, and automatically connects these new nodes to the active node in the RBF editor.
"""

import bpy
import math

from .. import var

## debug print variables for dev
debug_print__info = False
debug_print__node_add_nodes_input_from_selected_execute = False
debug_print__node_add_nodes_output_from_selected_execute = False
debug_print__rbf_tree_place_new_node = False


### ui functions ###
def menu_draw__add_multiple(self, context):
    """Draw the "Add multiple" submenu inside the "Add" menu, when appended to the desired menu using     bpy.types.NODE_MT_add.append(menus.menu_add_multiple_draw)"""
    layout = self.layout
    layout.menu("NODE_MT_add_multiple")


### other functions ###
def print_debug_info(context, tree):
    if not debug_print__info:
        return
    
    """print info that may be useful for developing or debugging the operators."""
    selected_objects = context.selected_objects
    selected_pose_bones = context.selected_pose_bones
    selected_bones = context.selected_bones
    if selected_bones:
        print("selected_bones: ", [b.name for b in selected_bones])
    if selected_pose_bones:
        print("selected_pose_bones: ", [o.name for o in selected_pose_bones])
    if selected_objects:
        print("selected_objects: ", [o.name for o in selected_objects])
        
    print("tree ", tree)
    
    if hasattr(tree, "nodes"):
        if hasattr(tree.nodes, "active"):
            print("active node ", tree.nodes.active)
    
    print("context.screen ", context.screen) # C.screen - current workspace screen
    
    space_node = context.space_data
    print("space_node ", space_node)
    
    if hasattr(space_node, "edit_tree"):
        node_tree = space_node.edit_tree
        print("node_tree (edit_tree) ", node_tree)
        
    if hasattr(context, "blend_data"):
        if hasattr(context.blend_data, "node_groups"):
            all_node_groups = context.blend_data.node_groups
            print("all_node_groups ", all_node_groups)
    
    print("context.scene.node_tree ", context.scene.node_tree)
    if hasattr(context.space_data, "node_tree"):
        if hasattr(context.space_data.node_tree, "active"):
            print("context.space_data.node_tree.nodes.active ", context.space_data.node_tree.nodes.active)
        else:
            print("context.space_data.node_tree has no 'active'")
    else:
        print("context.space_data has no 'node_tree'")
        pass
    pass


def edit_bone__get_owner_object(edit_bone_selected, selected_objects):
    """
    Returns the owner object for the selected edit bone.
    If user selected bones in Edit Mode, obtaining the owner object is a bit different than obtaining it from pose bones.
    "edit_bone.id_data" gives the bone's owner Armature, not the Object.
    But we know the Object is also selected, so we search for a selected object with same data as the seleced edit bone's data.
    Also works for multiple selected (Armature) Objects that are sharing the same Armature data:
    selecting multiple objects then switching to Edit mode and selecting an edit bone in one object also selects that bone in the other objects automatically.
    """
    edit_bone_armature_data = edit_bone_selected.id_data
    edit_bone_objects = [o for o in selected_objects if o.data == edit_bone_armature_data]
    if len(edit_bone_objects) > 0:
        return edit_bone_objects[0]
    return None


def get__objects_to_process_list__from_selected_objects(context):
    """Get formatted list of selected objects or pose bones, according to context and active/selected objects."""
    selected_bones = context.selected_bones
    selected_pose_bones = context.selected_pose_bones
    selected_objects = context.selected_objects

    ## generate list of objects/bones to add as nodes.
    ## Bone/Object selection hierarchy:
    ## if edit bones are selected, pose bones and objects selected are ignored (except those that contain the selected bones and are required).
    ## if pose bones are selected, objects are ignored (except those that contain the selected bones).
    ## if no edit or pose bones are selected, the selected objects are added.
    objects_to_process = []  # list of tuples to create nodes, each tuple is (object,bone) or just (object,)
    if selected_bones:
        for edit_bone in selected_bones:
            edit_bone_owner_object = edit_bone__get_owner_object(edit_bone, selected_objects)
            if edit_bone_owner_object:
                objects_to_process.append((edit_bone_owner_object, edit_bone.name))
    elif selected_pose_bones:
        for pbone in selected_pose_bones:
            objects_to_process.append((pbone.id_data, pbone.name))
    elif selected_objects:
        for obj in selected_objects:
            objects_to_process.append((obj, None))
            
    return objects_to_process


def get_rbf_required_data(context):
    from .. core.nodeTree import getNodeTree
    tree = getNodeTree(context)
    tree_node_active = None
    if hasattr(tree, "nodes") and hasattr(tree.nodes, "active"):
        tree_node_active = tree.nodes.active
    return tree, tree_node_active


def update_new_node_dimensions():
    """Update new node dimensions by forcing a ui redraw.
    Also remove the output to console of the "redraw_timer" functions because it's confusing."""
    import io
    from contextlib import redirect_stdout
    stdout = io.StringIO()
    with redirect_stdout(stdout):  # output to console will be muted for functions within this runtime context.
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)  # force redraw to update new node dimensions


def rbf_tree_place_new_node(node_new, rbf_node, new_node_is_input_node: bool):
    """Automatically places, in space, the newly created node inside the rbf tree editor."""
    
    if debug_print__rbf_tree_place_new_node:
        print("\nrbf_tree_place_new_node()")
        
    update_new_node_dimensions()
    
    ## add under the lowest input/output socket for the active rbf node
    rbf_node__lowest_connected_node = None
    if rbf_node:
        # n.outputs[0].links[n].to_node - the first 0 in outputs is fixed! it's the index of the socket, not of the output node.
        rbf_node__lowest_connected_node_y = math.inf
        if new_node_is_input_node:
            rbf_node__connected_nodes_links = rbf_node.inputs[0].links
            if debug_print__rbf_tree_place_new_node:
                print("rbf_node__connected_nodes_links (inputs) is ", rbf_node__connected_nodes_links)
        else:
            rbf_node__connected_nodes_links = rbf_node.outputs[0].links
            if debug_print__rbf_tree_place_new_node:
                print("rbf_node__connected_nodes_links (outputs) is ", rbf_node__connected_nodes_links)
            
        if debug_print__rbf_tree_place_new_node:
            print("searching for lowest connected node:")
        for connected_node_link in rbf_node__connected_nodes_links:
            if new_node_is_input_node:
                connected_node = connected_node_link.from_node
                if debug_print__rbf_tree_place_new_node:
                    print("using from_node")
            else:
                connected_node = connected_node_link.to_node
                if debug_print__rbf_tree_place_new_node:
                    print("using to_node")
                
            if debug_print__rbf_tree_place_new_node:
                print("checking connected node ", connected_node, " y:", connected_node.location.y, " prev ",
                  rbf_node__lowest_connected_node_y)
            if connected_node.location.y < rbf_node__lowest_connected_node_y:
                rbf_node__lowest_connected_node_y = connected_node.location.y
                rbf_node__lowest_connected_node = connected_node
                if debug_print__rbf_tree_place_new_node:
                    print("** updated lowest node to ", rbf_node__lowest_connected_node, " new y:", rbf_node__lowest_connected_node_y)
    
        if rbf_node__lowest_connected_node:
            if debug_print__rbf_tree_place_new_node:
                print("lowest connected node is ", rbf_node__lowest_connected_node)
                print("--lowest location: ", rbf_node__lowest_connected_node.location)
                print("--lowest dimensions: ", rbf_node__lowest_connected_node.dimensions)
            node_new.location.y = \
                rbf_node__lowest_connected_node.location.y - rbf_node__lowest_connected_node.dimensions.y - abs(
                    var.NODE_OFFSET[1])
            pass
        else:  # rbf node has not inputs, use it's own location
            node_new.location.y = \
                rbf_node.location.y
        pass
    
    ## position node in x
    if debug_print__rbf_tree_place_new_node:
        print("positioning in x:")
    
    ## if we found a previously added input/output node, use that node's x
    if rbf_node__lowest_connected_node:
        if debug_print__rbf_tree_place_new_node:
            print("adding to same x as lowest connected node ", rbf_node__lowest_connected_node ," which is ", rbf_node__lowest_connected_node.location.x)
        node_new.location.x = rbf_node__lowest_connected_node.location.x
    elif rbf_node:  # if no previously added node on that side, use the rbf node as reference
        if debug_print__rbf_tree_place_new_node:
            print("-no previously added input/output node, using rbf no as reference.")
            print("-tree_node_active.location.x ", rbf_node.location.x)
            print("-node_new.dimensions.x ", node_new.dimensions.x)
            print("-abs(var.NODE_OFFSET[0]) ", abs(var.NODE_OFFSET[0]))
    
        if new_node_is_input_node:  # input node, place to LEFT SIDE of rbf node
            node_new.location.x = \
                rbf_node.location.x - node_new.dimensions.x - abs(var.NODE_OFFSET[0])
        else:  # output node, place to RIGHT SIDE of rbf node
            node_new.location.x = \
                rbf_node.location.x + rbf_node.dimensions.x + abs(var.NODE_OFFSET[0])
            pass
        pass
    pass


def create_and_link_nodes_from_objects_to_process_list(create_input_node, objects_to_process, tree, tree_node_active):
    if not tree:
        print("no rbf node tree available (make sure one rbf node editor is open and an rbf node tree is selected). not adding nodes.")
        return {'FINISHED'}
    
    # process objects and create nodes
    for object_to_process in objects_to_process:
        obj = object_to_process[0]
        bone_name = object_to_process[1]
        
        node_new = None
        if create_input_node:
            node_new = tree.nodes.new("RBFObjectInputNode")
        else:
            node_new = tree.nodes.new("RBFObjectOutputNode")
        
        node_new.sceneObject = obj
        if bone_name:
            node_new.bone = bone_name
        
        rbf_tree_place_new_node(node_new, tree_node_active, create_input_node)
        
        # connect to active node in the RBF editor
        if tree_node_active:
            if create_input_node:
                tree.links.new(node_new.outputs[0], tree_node_active.inputs[0])
            else:
                tree.links.new(tree_node_active.outputs[0], node_new.inputs[0])


def rbf_nodes__create_nodes_from_selected_objects(context, create_input_node: bool):
    objects_to_process = get__objects_to_process_list__from_selected_objects(context)
    tree, tree_node_active = get_rbf_required_data(context)
    print_debug_info(context, tree)
    create_and_link_nodes_from_objects_to_process_list(
        create_input_node, objects_to_process, tree, tree_node_active)
    return {'FINISHED'}


def rbf__nodes__create_nodes_from_selected_objects__poll(context):
    """Fails if the operator is not being called from inside a nodetree editor,
    which is required for accessing a nodetree."""
    
    if not hasattr(context, "space_data"):
        print("node.add_nodes_input_from_selected poll() fail: context has no space_data. This operator must be run from inside the node tree editor!")
        return False
    if not hasattr(context.space_data, "node_tree"):
        print("node.add_nodes_input_from_selected poll() fail: context.space_data has no node_tree. This operator must be run from inside the node tree editor!")
        return False
    return True
