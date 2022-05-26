# <pep8 compliant>

import bpy

from . socket import RBFSocket
from .... import var


class RBFNodeSocket(bpy.types.NodeSocket, RBFSocket):
    """Object property socket"""
    bl_idname = "RBFNodeSocket"
    bl_label = "RBF Node Socket"

    color = var.COLOR_GREEN_2

    def draw(self, context, layout, node, text):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        :param node: The node the socket belongs to.
        :type node: bpy.types.Node
        :param text: The text label to draw alongside properties.
        :type text: str
        """
        layout.label(text=text)
