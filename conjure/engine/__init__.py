"""
Conjure engine package.

Contains:
- blender_server: Socket server for receiving commands
- cloud_bridge: WebSocket connection to Conjure cloud
- command_executor: Command routing and execution
"""

import bpy

from .blender_server import ConjureServer
from .command_executor import CommandExecutor

# Global server instance
_server = None


def get_server():
    """Get the global server instance."""
    global _server
    return _server


def start_server():
    """Start the Conjure server."""
    global _server
    if _server is None:
        prefs = bpy.context.preferences.addons.get("conjure")
        if prefs:
            prefs = prefs.preferences
            host = prefs.server_host
            port = prefs.server_port
        else:
            host = "127.0.0.1"
            port = 9877

        _server = ConjureServer(host=host, port=port)
        _server.start()
    return _server


def stop_server():
    """Stop the Conjure server."""
    global _server
    if _server is not None:
        _server.stop()
        _server = None


def register():
    """Register engine components."""
    # Auto-start server if preference is set
    prefs = bpy.context.preferences.addons.get("conjure")
    if prefs and prefs.preferences.auto_connect:
        # Delay start to after Blender is fully loaded
        bpy.app.timers.register(lambda: (start_server(), None)[1], first_interval=1.0)


def unregister():
    """Unregister engine components."""
    stop_server()
