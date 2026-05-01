#!/usr/bin/env python3
"""
Generate a standalone visualization HTML file that combines visualizer + data.

Usage:
    python3 generate-standalone-viz.py <path-to-results-dir>

Example:
    python3 generate-standalone-viz.py ./data/results/scenario-1/run-001/

This creates: wsn-uav-standalone.html (self-contained, no external files needed)
"""

import sys
import os
import json
import re
from pathlib import Path


def extract_json_from_js(js_content):
    """Extract JSON from JavaScript const WSN_UAV_DATA = {...}"""
    match = re.search(r'const\s+WSN_UAV_DATA\s*=\s*(\{[\s\S]*\});', js_content)
    if match:
        js_obj = match.group(1)
        # Convert JavaScript object to JSON by adding quotes to unquoted keys
        # This is a simple approach - works for the standard output format
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', js_obj)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse JSON: {e}")
            print(f"DEBUG: First 500 chars: {json_str[:500]}")
            return None
    return None


def generate_standalone_html(results_dir):
    """Generate standalone HTML with embedded data"""

    results_path = Path(results_dir).resolve()

    # Find the template in the ns-3 directory structure
    # Search upward for ns-3-dev-git-ns-3.46 directory
    current = results_path
    ns3_root = None
    while current != current.parent:
        if current.name.startswith('ns-3-dev'):
            ns3_root = current
            break
        current = current.parent

    if not ns3_root:
        print("ERROR: Could not find ns-3 root directory")
        return False

    html_template = ns3_root / "src/wsn-uav/examples/wsn-uav-visualizer.html"
    data_file = results_path / "visualization-data.js"

    if not html_template.exists():
        print(f"ERROR: Template not found: {html_template}")
        return False

    if not data_file.exists():
        print(f"ERROR: Data file not found: {data_file}")
        return False

    print(f"Reading data from: {data_file}")
    with open(data_file, 'r') as f:
        js_content = f.read()

    data = extract_json_from_js(js_content)
    if not data:
        print("ERROR: Could not extract JSON from visualization-data.js")
        return False

    print(f"Reading template from: {html_template}")
    with open(html_template, 'r') as f:
        html_content = f.read()

    # Embed data and override initialization
    # Simple approach: just append everything before closing body tag
    data_script = f'''
    <!-- Auto-embedded visualization data -->
    <script>
        {js_content.strip()}
        window.WSN_UAV_DATA_EMBEDDED = true;
    </script>

    <script>
        // Override visualizer initialization to use embedded data
        if (typeof visualizer !== 'undefined' && typeof WSN_UAV_DATA !== 'undefined') {{
            setTimeout(function() {{
                visualizer.data = WSN_UAV_DATA;
                visualizer.onDataLoaded();
                document.getElementById('fileInput').style.display = 'none';
                document.querySelector('.file-input-label').style.display = 'none';
                console.log('✓ Embedded visualization data loaded');
            }}, 50);
        }}
    </script>'''

    # Append data script before closing body
    modified_html = html_content.replace('</body>', data_script + '\n</body>')

    output_file = results_path / "wsn-uav-standalone.html"
    with open(output_file, 'w') as f:
        f.write(modified_html)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\n✓ Created: {output_file}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Usage: Open in browser (no dependencies needed)")
    print(f"\n  This file contains everything - no external files required!")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    results_dir = sys.argv[1]
    if not os.path.isdir(results_dir):
        print(f"ERROR: Directory not found: {results_dir}")
        sys.exit(1)

    success = generate_standalone_html(results_dir)
    sys.exit(0 if success else 1)
