# <pep8 compliant>

import bpy

from . import common, node
from ... core import driver
from ... ui import preferences


class RBFScaleOutputNode(node.RBFNode):
    """Driver object source.
    """
    bl_idname = "RBFScaleOutputNode"
    bl_label = "Scale"
    bl_icon = 'FIXED_SIZE'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    def updateCallback(self, context):
        """Callback for any value changes.

        :param context: The current context.
        :type context: bpy.context
        """
        pass

    x_axis : bpy.props.BoolProperty(name="X", default=False)
    y_axis : bpy.props.BoolProperty(name="Y", default=False)
    z_axis : bpy.props.BoolProperty(name="Z", default=False)

    output : bpy.props.FloatVectorProperty(update=updateCallback)
    # The indices of the created drivers on the driven object.
    driverIndex : bpy.props.IntVectorProperty(default=(-1, -1, -1))
    isDriver : bpy.props.BoolProperty(default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addInput("RBFPropertySocket", "Scale")
        
    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawTransformProperties(self, layout)

        if preferences.getPreferences().developerMode:
            col = layout.column(align=True)
            col.prop(self, "output")

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getProperties(self, obj):
        """Return the selected scale properties for the given object.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected scale properties and their
                 values as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getScaleProperties(self, obj)

    def getOutputProperties(self):
        """Return the selected output properties.

        :return: A list with the selected output properties and their
                 index as a tuple.
        :rtype: list(bpy.types.Node, int)
        """
        return common.getTransformOutputProperties(self)

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def createDriver(self, nodeGroup, driven, rbfNode):
        """Create a driver for each selected axis of the driven object.

        :param nodeGroup: The node tree of the current RBF setup.
        :type nodeGroup: bpy.types.NodeGroup
        :param driven: The driven object.
        :type driven: bpy.types.Object
        :param rbfNode: The current RBF node.
        :type rbfNode: bpy.types.Node
        """
        driver.createTransformDriver(self, nodeGroup, driven, "scale", rbfNode)

    def deleteDriver(self, obj):
        """Delete the driver for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        """
        driver.deleteTransformDriver(self, obj, "scale")

    def enableDriver(self, obj, enable):
        """Enable or disable the driver FCurves for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        :param enable: The enabled state of the driver FCurves.
        :type enable: bool
        """
        driver.enableDriver(self, obj, enable)
