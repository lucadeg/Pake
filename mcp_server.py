"""
Pake MCP Server for Hermes
Turn any webpage into a lightweight desktop app using Rust/Tauri.
"""
import json, os, subprocess, sys

SUPPORTED_TARGETS = ["windows", "macos", "linux", "macos-arm64", "macos-x86_64"]

def handle_create_desktop_app(args):
    url = args.get("url")
    name = args.get("name", "MyApp")
    if not url:
        return {"error": "url is required"}
    cmd = ["pake", url, "--name", name]
    icon = args.get("icon")
    if icon:
        cmd += ["--icon", icon]
    width = args.get("width")
    height = args.get("height")
    if width:
        cmd += ["--width", str(width)]
    if height:
        cmd += ["--height", str(height)]
    if args.get("fullscreen"):
        cmd.append("--fullscreen")
    if args.get("hide_title_bar"):
        cmd.append("--hide-title-bar")
    if args.get("multi_arch"):
        cmd.append("--multi-arch")
    targets = args.get("targets")
    if targets:
        cmd += ["--targets", targets]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

def handle_list_supported_targets(args):
    return {"targets": SUPPORTED_TARGETS}

def handle_get_app_config(args):
    name = args.get("name", "MyApp")
    return {
        "name": name,
        "url": args.get("url", ""),
        "width": args.get("width", 1200),
        "height": args.get("height", 780),
        "fullscreen": False,
        "hide_title_bar": False
    }

TOOLS = {
    "create_desktop_app": {
        "description": "Turn a webpage URL into a lightweight native desktop app using Pake (Rust/Tauri). ~20x smaller than Electron.",
        "parameters": {
            "url": {"type": "string", "description": "The webpage URL to wrap"},
            "name": {"type": "string", "description": "Application name"},
            "icon": {"type": "string", "description": "Path to app icon"},
            "width": {"type": "integer", "description": "Window width in pixels"},
            "height": {"type": "integer", "description": "Window height in pixels"},
            "fullscreen": {"type": "boolean", "description": "Start in fullscreen mode"},
            "hide_title_bar": {"type": "boolean", "description": "Hide the window title bar"},
            "multi_arch": {"type": "boolean", "description": "Build for multiple architectures"},
            "targets": {"type": "string", "description": "Target platform (windows, macos, linux)"}
        },
        "handler": handle_create_desktop_app
    },
    "list_supported_targets": {
        "description": "List all supported build targets for Pake desktop apps.",
        "parameters": {},
        "handler": handle_list_supported_targets
    },
    "get_app_config": {
        "description": "Get default or custom app configuration for a Pake build.",
        "parameters": {
            "name": {"type": "string", "description": "Application name"},
            "url": {"type": "string", "description": "Target URL"},
            "width": {"type": "integer", "description": "Window width"},
            "height": {"type": "integer", "description": "Window height"}
        },
        "handler": handle_get_app_config
    }
}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            method = req.get("method")
            if method == "tools/list":
                tools_list = []
                for name, t in TOOLS.items():
                    tools_list.append({"name": name, "description": t["description"], "inputSchema": {"type": "object", "properties": t["parameters"]}})
                print(json.dumps({"result": tools_list}), flush=True)
            elif method == "tools/call":
                tool_name = req.get("params", {}).get("name")
                arguments = req.get("params", {}).get("arguments", {})
                if tool_name in TOOLS:
                    result = TOOLS[tool_name]["handler"](arguments)
                    print(json.dumps({"result": result}), flush=True)
                else:
                    print(json.dumps({"error": f"Unknown tool: {tool_name}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    main()
