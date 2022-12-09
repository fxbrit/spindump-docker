## Build

To build the Docker image enter:
```
docker build -t fxbrit/spindump-docker
```

## Run

To run create the source bind directory using:
```
mkdir sdmp-vol
```

Then enter the following command to capture UDP traffic:
```
docker run -p 127.0.0.1:443:443 --mount type=bind,source="$(pwd)"/sdmp-vol,target=/workdir --name port-capture -ti fxbrit/spindump-docker
```

Or even:
```
docker run --net=host --mount type=bind,source="$(pwd)"/sdmp-vol,target=/workdir --name full-net-capture -ti fxbrit/spindump-docker
```