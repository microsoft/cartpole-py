# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# pull python packages from internal feed
COPY pip.conf /root/.pip/pip.conf

# Install SDK3 Python
RUN pip3 install -U setuptools

# Set up the simulator
WORKDIR /src

# Copy simulator files to /sim
COPY . /src

# Install wheel files for msft bonsai api
RUN pip3 install microsoft_bonsai_api-0.1-py3-none-any.whl

# Install dependencies
RUN pip3 install -r requirements.txt

# This will be the command to run the simulator
CMD ["python", "carptole.py"]
