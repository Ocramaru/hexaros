# syntax=docker/dockerfile:1
FROM ros:jazzy-ros-base

# keep downloaded .debs in the cache mounts between builds; the base image deletes them by default
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends python3-colcon-common-extensions i2c-tools

# rosdep's database comes before package.xml, so a dependency change doesn't refetch it; --no-cache refreshes it
RUN ([ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || rosdep init) && rosdep update

# install the package's dependencies from package.xml, so they're declared in one place
COPY src/hexapod/package.xml /tmp/deps/hexapod/package.xml
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && rosdep install --from-paths /tmp/deps --ignore-src -y && rm -rf /tmp/deps

ENV GPIOZERO_PIN_FACTORY=lgpio
WORKDIR /ws
