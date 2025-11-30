# Context-Fabric: Jetson Deployment Guide

## 1. Setup
1.  Copy `deploy_jetson.tar.gz` to each Jetson device.
2.  Extract: `tar -xzf deploy_jetson.tar.gz`
3.  Enter directory: `cd context-fabric`

## 2. Configuration
Edit `docker-compose.jetson.yml` on **each device** to set the correct environment variables:

-   **`LF_FEDERATION_ID`**: Must match the RTI's Federation ID.
-   **`LF_RTI_HOST`**: IP address of the machine running the RTI (e.g., your laptop).
-   **`LF_RTI_PORT`**: 15045 (default).
-   **`ROS_DOMAIN_ID`**: 42 (must match RTI machine).

**Important**: Ensure each device runs the correct service (`fed1` vs `fed2`).
-   On Jetson 1: Uncomment `fed1`, comment out `fed2`.
-   On Jetson 2: Uncomment `fed2`, comment out `fed1`.

## 3. Build
Build the Docker image on the Jetson (this takes time):
```bash
./dev.sh build
```

## 4. Run
Start the federate:
```bash
./dev.sh start
```

## 5. Monitor
To view logs:
```bash
./dev.sh logs fed1  # or fed2
```

To stop:
```bash
./dev.sh stop
```

## Troubleshooting
-   **Connection Refused**: Check `LF_RTI_HOST` and ensure RTI is running on central machine.
-   **Discovery Issues**: Ensure all devices are on the same subnet and `ROS_DOMAIN_ID` matches.

