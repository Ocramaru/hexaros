.PHONY: image shell ship build source bags replay record

PI := rpi4b
# the compose service for this machine: hexapod on the Pi, dev everywhere else
SERVICE ?= $(if $(filter $(PI),$(shell hostname)),hexapod,dev)
# the dev container runs as you, so what it builds stays yours
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)
# set inside the containers; outside, whichever ROS is installed
ROS_DISTRO ?= $(notdir $(firstword $(wildcard /opt/ros/*)))

# what `make record` keeps: the camera, the robot's pose and model, and every sensor
BAG_TOPICS := /camera/image_raw/compressed /camera/camera_info /tf /tf_static /joint_states /robot_description \
	/imu/data /imu/data_raw /ultrasonic/range /battery/pack0 /battery/pack1
BAG ?= $(lastword $(sort $(wildcard bags/*/)))

# build this machine's image
image:
	docker compose build $(SERVICE)

# a shell in this machine's container
shell:
	docker compose run --rm $(SERVICE) bash

# from sparky: build the Pi's image here and load it into the Pi's Docker, so the Pi never builds
ship:
	docker compose build hexapod
	docker save hexaros | ssh -C $(PI) docker load

# inside a container; sparky's own ROS and the containers' would overwrite each other's build/ and install/
build:
	colcon build --symlink-install --packages-select hexapod

# print the setup lines for your shell; make cannot change your terminal, so run: eval "$(make -s source)"
source:
	@shell=$$(basename $$SHELL); echo "source /opt/ros/$(ROS_DISTRO)/setup.$$shell"; [ -f install/setup.$$shell ] && echo "source install/setup.$$shell" || true

# list the recordings
bags:
	@ls -1d bags/*/ 2>/dev/null || echo "no recordings in bags/"

# play BAG (the newest by default) on a loop with its clock; `just bridge-replay` shows it in Foxglove
replay:
	$$SHELL -lc 'source /opt/ros/$(ROS_DISTRO)/setup.$$(basename $$SHELL) && ros2 bag play $(BAG) --loop --clock'

# on the Pi, alongside the running stack: record BAG_TOPICS into bags/ until Ctrl-C
record:
	docker compose run --rm hexapod bash -c 'source install/setup.bash && ros2 bag record -o bags/gerry_$$(date +%m%d_%H%M) $(BAG_TOPICS)'
