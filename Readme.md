# spindump-docker

Run [Spindump](https://github.com/EricssonResearch/spindump) in a Docker container to monitor QUIC traffic from the host machine.

## Build

To build the Docker image clone this repository and move into it:
```
git clone https://github.com/fxbrit/spindump-docker.git
cd spindump-docker
```

Then enter:
```
docker build . -t fxbrit/spindump-docker
```

## Run

:warning: :penguin: **the captures can only be performed on Linux hosts.**

First create the source bind directory:
```
mkdir spdmp-vol
```

Then start the container:
```
docker run -d --rm --net=host\
  --mount type=bind,source="$(pwd)"/spdmp-vol,target=/out\
  --name quic-capture fxbrit/spindump-docker
```

The output will be a set of QUIC captures, stored in `spdmp-vol/capture.json`.
