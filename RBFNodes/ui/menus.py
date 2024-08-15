import bpy
from bpy.types import Menu
from ..core import add_multiple


class NODE_MT_add_multiple(Menu):
    """Menu that displays the operators to create and link multiple nodes to a selected RBF node, taking from the selected objects.
    Usually added as a sub menu inside menu "Add" in the header of the RBF Nodes editor, added in the "register()" function of the __init__ file, appending the above "menu_draw__add_multiple" draw function to the existing "Add" menu.
    """
    bl_label = "Add multiple"
    
    def draw(self, context):
        self.layout.operator("node.add_nodes_input_from_selected")
        self.layout.operator("node.add_nodes_output_from_selected")
    
    @classmethod
    def register(cls):
        # add the "Add Multiple..." submenu to the "RBF Nodes" Editor -> header -> "Add" menu.
        bpy.types.NODE_MT_add.append(add_multiple.menu_draw__add_multiple)  # add the submenu "Add Multiple"
        # to the RBF Editor -> Header -> menu "Add"
        bpy.types.NODE_MT_context_menu.append(add_multiple.menu_draw__add_multiple)
        # add the submenu to the context menu, openable when pressing the W key inside the RBF editor
    
    @classmethod
    def unregister(cls):
        bpy.types.NODE_MT_context_menu.remove(add_multiple.menu_draw__add_multiple)  # remove the submenu from
        # the context menu, openable when pressing the W key inside the RBF editor
        bpy.types.NODE_MT_add.remove(add_multiple.menu_draw__add_multiple)  # remove the submenu "Add Multiple"
        # from the RBF Editor -> Header -> menu "Add"