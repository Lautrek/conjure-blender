"""
Conjure core package.

This package contains all the core functionality for the Conjure Blender add-on:
- operators: Blender operators for CAD operations
- panels: N-panel UI components
- engine: Socket server and command execution
- adapters: Blender-specific operation adapters
"""

from . import engine, operators, panels

# Track registered modules for cleanup
_registered_modules = []


def register():
    """Register all Conjure submodules."""
    # Order matters: engine first, then operators, then panels
    modules = [engine, operators, panels]

    for module in modules:
        if hasattr(module, "register"):
            module.register()
            _registered_modules.append(module)


def unregister():
    """Unregister all Conjure submodules."""
    # Reverse order for cleanup
    for module in reversed(_registered_modules):
        if hasattr(module, "unregister"):
            module.unregister()

    _registered_modules.clear()
