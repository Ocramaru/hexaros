---
name: learned
description: Workspace traps — ROS packages released but not installable, and files containers leave owned by root
kind: learned
---

# Learned

## Traps

- **A package listed as released in `rosdistro` can still be missing from apt.** `gscam` had a Lyrical release but no binary on either architecture, because its build farm job failed; check `packages.ros.org`'s index for the distro and architecture. The farm's logs sit behind a bot challenge, so test-compile in a throwaway container instead: gscam built cleanly in 9 s.
- **Containers write the workspace as root.** Builds and recordings came out root-owned and needed `sudo` to delete; the `dev` service runs as `HOST_UID`, while the Pi's stays root for its devices, so its `bags/` still need `sudo` or a container to remove.
