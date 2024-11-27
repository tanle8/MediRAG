# Using multi-stage builds to speed up image creation.
# There are two stages: builder and production stage.
# - Builder stage:
#       - Install all Python dependencies in a clean environment.
#       - Prevents unnecessary files from being copied into the final image.
# - Production stage:
#       - Copies only the necessary files and dependencies from the builder stage.

# BUILD STAGE
FROM python:3.10 as builder

# Set working directory
WORKDIR /app

# Copy only the requirements file to the image for caching
# This ensures that changes to the application code don't invalidate
# the Docker cache for dependencies.
COPY ./requirements.txt /app/requirements.txt

# Install dependencies in a separate layer for caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./webapp/ /app/webapp

# PRODUCTION STAGE
# Use python:3.10-slim in the final stage, significantly  reducing image size compared
# to python:3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin
# COPY --from=builder /app /webapp

# Copy application code
COPY --from=builder /app /app

# Expose the application port
EXPOSE 80

# Command to run the application
# Define the entrypoint and command
# ENTRYPOINT ["uvicorn"]
# CMD ["main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "80"]

