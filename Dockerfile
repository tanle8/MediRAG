 FROM python:3.10

# Copy the requirements file to the image
COPY ./requirements.txt /webapp/requirements.txt

# Use a suitable working directory
WORKDIR /webapp

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY webapp/* /webapp

# Define the entrypoint and command
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "80"]
