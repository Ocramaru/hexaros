# syntax=docker/dockerfile:1
ARG ROS_DISTRO=lyrical

# robot: what Gerry's Pi runs
FROM ros:${ROS_DISTRO}-ros-base AS robot

# keep downloaded .debs in the cache mounts between builds; the base image deletes them by default
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends python3-colcon-common-extensions i2c-tools make

# rosdep's database comes before package.xml, so a dependency change doesn't refetch it; --no-cache refreshes it
RUN ([ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || rosdep init) && rosdep update

# gscam has no Lyrical binary yet (its build farm job fails), so it is built here into /opt/ros like the package would be;
# drop this step and --skip-keys once ros-lyrical-gscam installs
ARG GSCAM_COMMIT=20d7743dd09f05db6bf245a874597a65ba20a99c
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends git libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
      ros-${ROS_DISTRO}-camera-info-manager ros-${ROS_DISTRO}-image-transport ros-${ROS_DISTRO}-cv-bridge ros-${ROS_DISTRO}-rclcpp-components \
    && git clone https://github.com/ros-drivers/gscam.git /tmp/gscam && git -C /tmp/gscam checkout ${GSCAM_COMMIT} \
    && . /opt/ros/${ROS_DISTRO}/setup.sh \
    && cmake -S /tmp/gscam -B /tmp/gscam/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/ros/${ROS_DISTRO} \
    && cmake --build /tmp/gscam/build --target install -j "$(nproc)" && rm -rf /tmp/gscam

# install the package's dependencies from package.xml, so they're declared in one place
COPY src/hexapod/package.xml /tmp/deps/hexapod/package.xml
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && rosdep install --from-paths /tmp/deps --ignore-src -y --skip-keys gscam && rm -rf /tmp/deps

ENV GPIOZERO_PIN_FACTORY=lgpio
WORKDIR /ws

# dev: the robot image plus what sparky runs around it
FROM robot AS dev
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends ros-${ROS_DISTRO}-foxglove-bridge
