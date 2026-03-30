# Use Ubuntu 22.04
FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    apt-get clean

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Unified Planning and TAMER
RUN pip install unified-planning up-tamer

# Set working directory
WORKDIR /home/CS378_hw3

# Copy your homework files into the container
COPY . /home/CS378_hw3

# Default command when container runs
CMD ["python3", "modeling.py"]