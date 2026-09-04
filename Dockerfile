# Red Hat's supported Python 3.11 image. It already includes Python and pip
# and runs as a non-root user, which is exactly what OpenShift expects.
FROM registry.access.redhat.com/ubi9/python-311

# Install dependencies first so this layer is cached between builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code in.
COPY app.py .
COPY templates ./templates
COPY static ./static

# The app listens on port 5000.
EXPOSE 5000

# Point Flask at our app and have it listen on all interfaces.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start the web server.
CMD ["flask", "run"]
