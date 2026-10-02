FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3-colcon-common-extensions i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# install the package's dependencies from package.xml, so they're declared in one place
COPY src/hexapod/package.xml /tmp/deps/hexapod/package.xml
RUN apt-get update \
    && ([ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || rosdep init) \
    && rosdep update \
    && rosdep install --from-paths /tmp/deps --ignore-src -y \
    && rm -rf /var/lib/apt/lists/* /tmp/deps

ENV GPIOZERO_PIN_FACTORY=lgpio
WORKDIR /ws

