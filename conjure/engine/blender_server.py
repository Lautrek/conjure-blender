"""
Conjure Blender Server - Thin Client

Socket server that runs inside Blender and executes primitive CAD commands.
All orchestration and business logic happens on the hosted server.
This client only receives and executes low-level commands.

Supported command types:
- Primitives: create_cube, create_sphere, create_cylinder, create_cone, create_torus
- Curves: create_bezier, create_nurbs, create_path
- Booleans: boolean_union, boolean_difference, boolean_intersect
- Transforms: move_object, rotate_object, scale_object, copy_object, delete_object
- Modifiers: add_modifier, remove_modifier, apply_modifier
- Geometry Nodes: create_node_group, add_node, connect_nodes
- Materials: create_material, assign_material
- Animation: insert_keyframe, create_armature
- Physics: add_rigid_body, add_cloth, add_fluid, bake_physics
- Queries: get_state, list_objects, get_object_details, measure_distance
- Export: export_stl, export_obj, export_fbx, export_gltf
- View: set_view, capture_viewport
"""

import contextlib
import json
import queue
import socket
import sys
import threading
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import bpy

from .command_executor import CommandExecutor

# Add shared module to path for material client
_shared_path = Path(__file__).parent.parent.parent.parent / "shared"
if str(_shared_path) not in sys.path:
    sys.path.insert(0, str(_shared_path))

try:
    from materials import MaterialsClient
except ImportError:
    MaterialsClient = None  # Will use fallback


class ConjureServer:
    """Thin socket server for Blender command execution."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9877,
        server_url: str = "http://localhost:8000",
    ):
        self.host = host
        self.port = port
        self.server_url = server_url
        self.running = False
        self.socket: Optional[socket.socket] = None
        self.client: Optional[socket.socket] = None
        self.thread: Optional[threading.Thread] = None

        # Thread-safe operation queue for main thread execution
        self.operation_queue: queue.Queue = queue.Queue()
        self.result_map: Dict[str, Any] = {}
        self.result_events: Dict[str, threading.Event] = {}

        # Materials client for engineering materials
        self.materials_client: Optional[MaterialsClient] = None
        if MaterialsClient:
            try:
                self.materials_client = MaterialsClient(server_url)
            except Exception as e:
                print(f"Conjure: Failed to initialize materials client: {e}")

        # Command executor with materials client
        self.executor = CommandExecutor(materials_client=self.materials_client)

        # Timer for processing queue on main thread
        self._timer_registered = False

        # Adapter info for capability registration
        self.adapter_id = f"blender_{uuid.uuid4().hex[:8]}"
        self.adapter_type = "blender"
        self.blender_version = ".".join(str(v) for v in bpy.app.version)

    def start(self):
        """Start the server in background thread."""
        if self.running:
            print("Conjure: Server already running")
            return

        self.running = True

        # Start queue processor timer
        if not self._timer_registered:
            bpy.app.timers.register(self._process_queue, persistent=True)
            self._timer_registered = True

        # Start server thread
        self.thread = threading.Thread(target=self._server_loop, daemon=True)
        self.thread.start()

        print(f"Conjure: Server started on {self.host}:{self.port}")
        print(f"Conjure: Adapter ID: {self.adapter_id}")

    def stop(self):
        """Stop the server."""
        self.running = False

        # Stop timer
        if self._timer_registered:
            try:
                bpy.app.timers.unregister(self._process_queue)
            except Exception:
                pass
            self._timer_registered = False

        # Close sockets
        if self.client:
            with contextlib.suppress(Exception):
                self.client.close()
            self.client = None

        if self.socket:
            with contextlib.suppress(Exception):
                self.socket.close()
            self.socket = None

        print("Conjure: Server stopped")

    def _server_loop(self):
        """Main server loop - accepts connections and handles commands."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.socket.settimeout(1.0)
        except OSError as e:
            print(f"Conjure: Failed to bind to {self.host}:{self.port} - {e}")
            self.running = False
            return

        while self.running:
            try:
                self.client, addr = self.socket.accept()
                print(f"Conjure: Client connected from {addr}")
                self._update_connection_status(True)
                self._handle_client()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Conjure: Server error: {e}")

    def _handle_client(self):
        """Handle commands from connected client."""
        buffer = ""

        while self.running and self.client:
            try:
                data = self.client.recv(8192).decode("utf-8")
                if not data:
                    break

                buffer += data

                # Process complete messages (newline-delimited JSON)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        response = self._execute_command(line.strip())
                        response_str = json.dumps(response) + "\n"
                        self.client.send(response_str.encode("utf-8"))

            except Exception as e:
                print(f"Conjure: Client error: {e}")
                break

        if self.client:
            self.client.close()
            self.client = None
            self._update_connection_status(False)
            print("Conjure: Client disconnected")

    def _execute_command(self, command_str: str) -> Dict[str, Any]:
        """Parse and execute a command."""
        try:
            cmd = json.loads(command_str)
            cmd_type = cmd.get("type", "")
            params = cmd.get("params", {})
            request_id = cmd.get("request_id", str(uuid.uuid4()))

            # Queue operation for main thread execution
            result = self._queue_operation(cmd_type, params, request_id)
            return result

        except json.JSONDecodeError as e:
            return {"status": "error", "error": f"Invalid JSON: {e}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _queue_operation(self, cmd_type: str, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Queue an operation for main thread execution and wait for result."""
        # Create event for this request
        event = threading.Event()
        self.result_events[request_id] = event

        # Queue the operation
        self.operation_queue.put((cmd_type, params, request_id))

        # Wait for result (timeout after 60 seconds)
        if event.wait(timeout=60.0):
            result = self.result_map.pop(request_id, None)
            del self.result_events[request_id]
            return result if result else {"status": "error", "error": "No result"}
        else:
            del self.result_events[request_id]
            return {"status": "error", "error": "Operation timed out"}

    def _process_queue(self) -> Optional[float]:
        """Process operations on main thread (called by Blender timer)."""
        if not self.running:
            return None  # Unregister timer

        # Process up to 10 operations per timer call
        for _ in range(10):
            try:
                cmd_type, params, request_id = self.operation_queue.get_nowait()

                # Execute command via executor
                try:
                    result = self.executor.execute(cmd_type, params)
                except Exception as e:
                    result = {"status": "error", "error": str(e)}

                # Store result and signal waiting thread
                self.result_map[request_id] = result
                if request_id in self.result_events:
                    self.result_events[request_id].set()

            except queue.Empty:
                break

        # Continue timer (return interval in seconds)
        return 0.05  # 50ms interval

    def _update_connection_status(self, connected: bool):
        """Update connection status in scene properties."""
        try:
            if bpy.context.scene:
                bpy.context.scene.conjure.is_connected = connected
                bpy.context.scene.conjure.adapter_id = self.adapter_id if connected else ""
                bpy.context.scene.conjure.server_status = "connected" if connected else "disconnected"
        except Exception:
            pass  # Scene might not be available during startup/shutdown

    def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities for registration with the Conjure server."""
        # Detect GPU availability
        gpu_available = self._detect_gpu_capabilities()

        return {
            "adapter_type": self.adapter_type,
            "adapter_id": self.adapter_id,
            "version": "1.0.0",
            "blender_version": self.blender_version,
            "capabilities": {
                "cad_operations": [
                    "primitives",
                    "curves",
                    "booleans",
                    "transforms",
                    "modifiers",
                    "geometry_nodes",
                    "materials",
                    "animation",
                    "armatures",
                    "shape_keys",
                    "queries",
                    "export",
                ],
                "simulation": {
                    "physics": {
                        "supported": True,
                        "types": ["rigid_body", "soft_body", "cloth", "fluid"],
                        "gpu_accelerated": gpu_available.get("cycles", False),
                        "realtime_capable": True,
                        "fidelity_levels": ["QUICK", "STANDARD", "DETAILED"],
                    },
                    "dynamic_properties": {
                        "supported": True,
                        "mass_calculation": True,
                        "volume_calculation": True,
                        "center_of_mass": True,
                        "moments_of_inertia": True,
                        "surface_area": True,
                    },
                    "heat_transfer": {
                        "supported": False,
                        "note": "Use server-side ThermalEstimator",
                    },
                    "flow_analysis": {
                        "supported": False,
                        "note": "Use server-side FluidEstimator",
                    },
                    "structural": {
                        "supported": False,
                        "note": "Use server-side BeamEstimator",
                    },
                },
                "animation": {
                    "keyframes": True,
                    "armatures": True,
                    "shape_keys": True,
                    "constraints": True,
                    "drivers": True,
                    "nla_editor": True,
                },
                "geometry_kernels": ["mesh", "nurbs", "curve", "gpencil"],
                "export_formats": ["STL", "OBJ", "FBX", "glTF", "USD", "PLY", "ABC"],
                "import_formats": ["STL", "OBJ", "FBX", "glTF", "USD", "PLY", "ABC", "DAE"],
                "streaming_results": True,
            },
            "resource_limits": {
                "max_memory_mb": self._get_available_memory(),
                "max_simulation_time_seconds": 3600,
                "concurrent_simulations": 1,
                "max_vertices": 10_000_000,
                "max_objects": 10_000,
            },
            "gpu_info": gpu_available,
            "system_info": {
                "os": sys.platform,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
        }

    def _detect_gpu_capabilities(self) -> Dict[str, Any]:
        """Detect available GPU capabilities for simulation."""
        gpu_info = {
            "available": False,
            "cycles": False,
            "eevee": True,  # Always available
            "devices": [],
        }

        try:
            # Check Cycles GPU availability
            prefs = bpy.context.preferences
            cycles_prefs = prefs.addons.get("cycles")

            if cycles_prefs:
                cycles_prefs = cycles_prefs.preferences
                compute_device_type = cycles_prefs.compute_device_type

                if compute_device_type in ("CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"):
                    gpu_info["available"] = True
                    gpu_info["cycles"] = True
                    gpu_info["compute_type"] = compute_device_type

                    # Get device info
                    for device in cycles_prefs.devices:
                        if device.type != "CPU":
                            gpu_info["devices"].append(
                                {
                                    "name": device.name,
                                    "type": device.type,
                                    "use": device.use,
                                }
                            )

        except Exception:
            pass  # GPU detection failed, use defaults

        return gpu_info

    def _get_available_memory(self) -> int:
        """Get available system memory in MB."""
        try:
            import os

            if hasattr(os, "sysconf"):
                # Linux/Unix
                pages = os.sysconf("SC_PHYS_PAGES")
                page_size = os.sysconf("SC_PAGE_SIZE")
                return (pages * page_size) // (1024 * 1024)
        except Exception:
            pass
        return 8192  # Default 8GB

    def register_with_server(self) -> bool:
        """Register this client's capabilities with the Conjure cloud server."""
        import urllib.error
        import urllib.request

        capabilities = self.get_capabilities()

        registration_payload = {
            "adapter_id": self.adapter_id,
            "adapter_type": self.adapter_type,
            "host": self.host,
            "port": self.port,
            "capabilities": capabilities,
            "status": "available",
        }

        try:
            # Send registration to server
            url = f"{self.server_url}/api/v1/adapters/register"
            data = json.dumps(registration_payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("status") == "registered":
                    print(f"Conjure: Registered with server as {self.adapter_id}")
                    return True

        except urllib.error.URLError as e:
            print(f"Conjure: Server registration failed (server offline?): {e}")
        except Exception as e:
            print(f"Conjure: Registration error: {e}")

        return False

    def deregister_from_server(self) -> bool:
        """Deregister this client from the Conjure cloud server."""
        import urllib.error
        import urllib.request

        try:
            url = f"{self.server_url}/api/v1/adapters/{self.adapter_id}/deregister"
            req = urllib.request.Request(url, method="POST")

            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("status") == "deregistered":
                    print("Conjure: Deregistered from server")
                    return True

        except Exception as e:
            print(f"Conjure: Deregistration error: {e}")

        return False

    def send_heartbeat(self) -> bool:
        """Send heartbeat to keep registration alive."""
        import urllib.error
        import urllib.request

        try:
            url = f"{self.server_url}/api/v1/adapters/{self.adapter_id}/heartbeat"
            data = json.dumps(
                {
                    "status": "available",
                    "active_jobs": 0,
                    "memory_usage_mb": self._get_current_memory_usage(),
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200

        except Exception:
            return False

    def _get_current_memory_usage(self) -> int:
        """Get current Blender memory usage in MB."""
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            return usage.ru_maxrss // 1024  # Convert KB to MB
        except Exception:
            return 0
