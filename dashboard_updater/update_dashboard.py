from jinja2 import Template
import json

# File paths (MUST match the volume mounts exactly)
THRESHOLDS_PATH = 'shared_file/thresholds.json'
TEMPLATE_PATH = 'grafana_dashboard_template.json'
OUTPUT_PATH = 'dashboards/updated_dashboard.json'

# Load files
with open(THRESHOLDS_PATH) as f:
    shared_data = json.load(f)

with open(TEMPLATE_PATH) as f:
    template_data = f.read()

# Render and save
template = Template(template_data)
rendered = template.render(thresholds=shared_data)

with open(OUTPUT_PATH, 'w') as f:
    f.write(rendered)

print("Dashboard rendered successfully to", OUTPUT_PATH)