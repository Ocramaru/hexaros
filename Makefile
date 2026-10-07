.PHONY: build source bags replay record

# what `make record` keeps: the camera, the robot's pose and model, and every sensor
BAG_TOPICS := /camera/image_raw/compressed /camera/camera_info /tf /tf_static /joint_states /robot_description \
	/imu/data /imu/data_raw /ultrasonic/range /battery/pack0 /battery/pack1
BAG ?= $(lastword $(sort $(wildcard bags/*/)))

build:
	colcon build --symlink-install --packages-select hexapod

# print the setup lines for your shell; make cannot change your terminal, so run: eval "$(make -s source)"
source:
	@shell=$$(basename $$SHELL); echo "source /opt/ros/jazzy/setup.$$shell"; [ -f install/setup.$$shell ] && echo "source install/setup.$$shell" || true

# list the recordings
bags:
	@ls -1d bags/*/ 2>/dev/null || echo "no recordings in bags/"

# play BAG (the newest by default) on a loop with its clock; `just bridge-replay` shows it in Foxglove
replay:
	$$SHELL -lc 'source /opt/ros/jazzy/setup.$$(basename $$SHELL) && ros2 bag play $(BAG) --loop --clock'

# on the Pi, alongside the running stack: record BAG_TOPICS into bags/ until Ctrl-C
record:
	docker compose run --rm hexapod bash -c 'source install/setup.bash && ros2 bag record -o bags/gerry_$$(date +%m%d_%H%M) $(BAG_TOPICS)'
