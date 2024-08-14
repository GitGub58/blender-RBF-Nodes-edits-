Addition to the "RBF Nodes" addon.


Adds two new Operators to the RBF Nodes editor, to allow creating multiple Input/Output Nodes automatically from all selected Objects or Bones, and automatically connecting these new nodes to the active node in the RBF editor.
Also adds a new menu "Add multiple" to contain these operators, as a submenu to the header's "Add" menu.


The new Operators are called:
    "Objects Input Nodes (Selected)" - bpy.ops.node.add_nodes_input_from_selected() 
    and 
    "Objects Output Nodes (Selected)" - bpy.ops.node.add_nodes_output_from_selected()

These new Operators are present in the RBF Nodes editor, in:
    . Header -> menu "Add" -> "Add multiple" -> "Objects Input Nodes (Selected)"/"Objects Output Nodes (Selected)".
    . Context Menu (by pressing "W" by default) -> "Add Multiple" -> (operators names)
    . Add menu (by pressing Shift+A by default) -> "Add Multiple" -> (operators names)
    . search Menu (by pressing Space) -> "Add Multiple" -> (operators names)


Usage example:
- Open rbf editor in one of the window areas.
- Create and select an rbf nodes tree in that editor. 
- In another editor area, such as 3d view or Outliner, select one or multiple objects, or pose bones for one or multiple armatures, or even edit bones. (To select bones from different armatures, first select the armature objects in Object Mode, then switch to Pose mode or Edit Mode, then select the bones from the multiple armatures).
- Go back to RBF Editor Area, and in that, ensure the RBF Node is selected, and in the header -> Add -> "Add multiple". Multiple Input (or Output) Nodes will be created, with their "Object" and "Bone" fields filled, and automatically linked to the corresponding slot in the active node in the RBF node editor. 



NOTE FOR DEVELOPERS:
Due to these operators being dependent on an open and visible RBF Nodes Editor, with an existing and present Node Tree, the operators will fail to be run from the console (can only be invoked while inside the RBF editor area itself).
