## Build

To build the Docker image enter:
```
docker build . -t fxbrit/spindump-docker
```

## Run

To run create the source bind directory using:
```
mkdir spdmp-vol
```

Then enter the following command:
```
docker run -d --rm --net=host --mount type=bind,source="$(pwd)"/spdmp-vol,target=/out --name full-net-capture fxbrit/spindump-docker
```

The output will be a set of QUIC captures, stored in `spdmp-vol/capture.json`.

**WARNING: the captures can be performed  exclusively on Linux.**

