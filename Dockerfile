FROM ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Runtime libraries for OpenCV/Ultralytics and a few utilities that make
# interactive debugging inside the container less painful.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ros-humble-geometry-msgs \
    ros-humble-std-msgs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# rclpy is provided by the ROS base image; installing it from pip is usually
# unnecessary and often fails, so install the remaining Python dependencies.
RUN python3 -m pip install --upgrade pip && \
    grep -v '^rclpy$' requirements.txt > /tmp/requirements.txt && \
    python3 -m pip install -r /tmp/requirements.txt

COPY . .

# The repository currently mixes standalone scripts with an incomplete ROS 2
# package layout, so default to an interactive shell rather than forcing a
# startup command that may fail without local image/device setup.
CMD ["/bin/bash"]