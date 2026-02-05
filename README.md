# Conjure Blender Add-on

Blender add-on for AI-assisted 3D modeling with Conjure. Enables Claude Code and other AI tools to control Blender via the Model Context Protocol (MCP).

## Features

- AI-assisted 3D modeling via natural language
- Full Blender API access through MCP tools
- Geometry Nodes support
- Physics simulation control
- Materials and rendering
- Animation and keyframing
- Works with Claude Code out of the box

## Requirements

- Blender 4.2+
- Python 3.11+ (bundled with Blender)

## Installation

### Option 1: Blender Preferences (Recommended)

1. Download the latest release ZIP from [Releases](https://github.com/Lautrek/conjure-blender/releases)
2. Open Blender
3. Go to **Edit > Preferences > Add-ons**
4. Click **Install...** and select the downloaded ZIP
5. Enable the "Conjure" add-on
6. Restart Blender

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/Lautrek/conjure-blender.git

# Copy to Blender addons directory
# Linux:
cp -r conjure-blender ~/.config/blender/4.2/scripts/addons/conjure

# macOS:
cp -r conjure-blender ~/Library/Application\ Support/Blender/4.2/scripts/addons/conjure

# Windows:
# Copy to %APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\conjure
```

## Quick Start

1. **Start Blender** with the Conjure add-on enabled
2. **Configure Claude Code** to use the Conjure MCP server:

Edit `~/.claude/workspace-settings.json`:
```json
{
  "mcpServers": {
    "conjure": {
      "command": "blender",
      "args": ["--background", "--python-expr", "import conjure; conjure.start_server()"]
    }
  }
}
```

3. **Start creating** with natural language:
```
"Create a cube with a subdivision modifier and apply a metallic material"
```

## Configuration

Create `~/.conjure/config.yaml`:

```yaml
# Blender connection
blender:
  host: localhost
  port: 9877

# Optional: Connect to Conjure cloud server
server:
  enabled: false
  url: https://api.conjure.lautrek.com
  api_key: sk-your-api-key
```

## Architecture

```
Claude Code (Editor)
    | (MCP stdio)
Conjure Add-on (Blender)
    |-> 3D Operations (local)
    \-> (Optional) Cloud Server
```

The add-on:
- Receives MCP tool calls from Claude Code
- Executes operations directly in Blender
- Supports Geometry Nodes, physics, materials, animation
- Optionally syncs with cloud server for collaboration

## Available Operations

### Primitives
- `create_cube`, `create_sphere`, `create_cylinder`, `create_cone`, `create_torus`, `create_plane`

### Curves
- `create_bezier`, `create_nurbs`, `create_path`

### Booleans
- `boolean_union`, `boolean_difference`, `boolean_intersect`

### Transforms
- `move_object`, `rotate_object`, `scale_object`, `copy_object`, `delete_object`

### Modifiers
- `add_modifier`, `remove_modifier`, `apply_modifier`
- `add_bevel`, `add_solidify`, `add_mirror`, `add_array`, `add_subdivision`

### Materials
- `create_material`, `assign_material`, `list_engineering_materials`

### Animation
- `insert_keyframe`, `create_armature`, `set_frame_range`, `play_animation`

### Physics
- `add_rigid_body`, `add_cloth`, `add_soft_body`, `add_fluid_domain`, `bake_physics`

### Rendering
- `render_image`, `set_render_engine`, `set_render_resolution`, `create_studio_lighting`

### Geometry Nodes
- `create_node_group`, `add_node`, `connect_nodes`, `set_node_input`, `apply_node_group`

### Export
- `export_stl`, `export_obj`, `export_gltf`, `export_fbx`

## Development

```bash
# Clone the repo
git clone https://github.com/Lautrek/conjure-blender.git
cd conjure-blender

# Run linting
pip install ruff
ruff check .

# Install as symlink for development
ln -s $(pwd) ~/.config/blender/4.2/scripts/addons/conjure
```

## Project Structure

```
conjure-blender/
├── __init__.py              # Blender add-on entry point
├── blender_manifest.toml    # Blender 4.2+ extension manifest
├── conjure/                  # Core module
│   ├── adapters/            # Blender operation adapters
│   ├── engine/              # Server and execution engine
│   ├── operators/           # Blender operators
│   ├── panels/              # UI panels
│   └── utils/               # Utility functions
├── assets/                   # Icons and images
└── config.example.yaml      # Example configuration
```

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

MIT License - See [LICENSE](LICENSE) file.

## Links

- [Conjure SDK](https://github.com/Lautrek/conjure-sdk) - Python SDK for Conjure
- [Conjure FreeCAD](https://github.com/Lautrek/conjure-freecad) - FreeCAD workbench
- [Documentation](https://lautrek.com/conjure/docs)
- [Issues](https://github.com/Lautrek/conjure-blender/issues)
