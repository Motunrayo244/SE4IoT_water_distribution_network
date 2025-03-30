FROM python:3.9-slim

# Install dependencies
RUN pip install jinja2

# Set working directory
WORKDIR /app

# Copy only necessary files (relative to build context)
COPY dashboard_updater/grafana_dashboard_template.json .
COPY dashboard_updater/update_dashboard.py .

# Runtime command
CMD ["python", "update_dashboard.py"]