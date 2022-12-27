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

## Pull

The image is [available on Docker Hub](https://hub.docker.com/r/fxbrit/spindump-docker) so you can use:
```
docker pull fxbrit/spindump-docker
```

## Run

:warning: :penguin: **the captures can only be performed on Linux hosts.**

Once you built or pulled the image, create the source bind directory using:
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

### Options

By using `ENV` variables it is possible to customize captures. In particular:
- `INTERFACE`: allows to specify the name of the host interface that we want to monitor.
  By default it will monitor all interfaces.
- `MAX_RECEIVE`: allows to set a limit to the maximum number of packets in the capture.
  By default there is no limit.
- `SOURCE_IP`: allows to filter by source IP address or source IP network.
  Accepts both IPv4 and IPv6 addresses.
- `DEST_IP`: allows to filter by destination IP address or destination IP network.
  Accepts both IPv4 and IPv6 addresses.

These variables are mapped to specific [Spindump options](https://github.com/EricssonResearch/spindump/blob/master/Usage.md).

### Usage examples

If we want to monitor the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host\
  --mount type=bind,source="$(pwd)"/spdmp-vol,target=/out\
  -e "INTERFACE=wlp3s0"\
  --name quic-capture fxbrit/spindump-docker
```

If we want to monitor traffic going to the network `192.168.1.0/24`
via the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host\
  --mount type=bind,source="$(pwd)"/spdmp-vol,target=/out\
  -e "INTERFACE=wlp3s0"\
  -e "DEST_IP=192.168.1.0/24"\
  --name quic-capture fxbrit/spindump-docker
```

If we want to monitor traffic going from the host `192.168.2.128` to
the nextwork `192.168.1.0/24` via the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host\
  --mount type=bind,source="$(pwd)"/spdmp-vol,target=/out\
  -e "INTERFACE=wlp3s0"\
  -e "SOURCE_IP=192.168.2.128"\
  -e "DEST_IP=192.168.1.0/24"\
  --name quic-capture fxbrit/spindump-docker
```
