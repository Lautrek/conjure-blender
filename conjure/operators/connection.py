"""
Connection operators for Conjure.

Operators for managing connection to Conjure server.
"""

import bpy
from bpy.types import Operator


class CONJURE_OT_connect(Operator):
    """Connect to Conjure server."""

    bl_idname = "conjure.connect"
    bl_label = "Connect"
    bl_description = "Connect to Conjure server"

    def execute(self, context):
        from ..engine import get_server, start_server

        server = get_server()
        if server and server.running:
            self.report({"INFO"}, "Already connected")
            return {"CANCELLED"}

        start_server()
        self.report({"INFO"}, "Connected to Conjure server")
        return {"FINISHED"}


class CONJURE_OT_disconnect(Operator):
    """Disconnect from Conjure server."""

    bl_idname = "conjure.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect from Conjure server"

    def execute(self, context):
        from ..engine import get_server, stop_server

        server = get_server()
        if not server or not server.running:
            self.report({"INFO"}, "Not connected")
            return {"CANCELLED"}

        stop_server()
        self.report({"INFO"}, "Disconnected from Conjure server")
        return {"FINISHED"}


class CONJURE_OT_test_connection(Operator):
    """Test connection to Conjure server."""

    bl_idname = "conjure.test_connection"
    bl_label = "Test Connection"
    bl_description = "Test connection to Conjure server"

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if server and server.running:
            self.report({"INFO"}, f"Connected: {server.host}:{server.port}")
            context.scene.conjure.server_status = "connected"
        else:
            self.report({"WARNING"}, "Not connected")
            context.scene.conjure.server_status = "disconnected"

        return {"FINISHED"}
