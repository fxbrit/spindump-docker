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
docker run -d --rm --net=host \
  -v "$(pwd)"/out:/out \
  --name quic-capture fxbrit/spindump-docker
```

The output will be a set of QUIC captures, stored in `spdmp-vol/capture.json`.

### Options

By using `ENV` variables it is possible to customize captures. In particular:
- `INTERFACE`: allows to specify the name of the host interface that we want to monitor.
  By default it will monitor all interfaces.
- `MAX_RECEIVE`: allows to set a limit to the maximum number of packets in the capture.
  By default there is no limit.
- `FILTERS`: allows to specify extra [PCAP filters](https://linux.die.net/man/7/pcap-filter).
  Always use `and` at the start of a filter.

These variables are mapped to specific [Spindump options](https://github.com/EricssonResearch/spindump/blob/master/Usage.md).

### Usage examples

If we want to monitor the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host \
  -v "$(pwd)"/out:/out \
  -e "INTERFACE=wlp3s0" \
  --name quic-capture fxbrit/spindump-docker
```

If we want to monitor traffic going to the network `142.250.0.0/16`
via the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host \
  -v "$(pwd)"/out:/out \
  -e "INTERFACE=wlp3s0" \
  -e "FILTERS=and dst net 142.250.0.0/16" \
  --name quic-capture fxbrit/spindump-docker
```

If we want to monitor traffic going from the host `192.168.2.128` to
the network `142.250.0.0/16` via the interface `wlp3s0` we can use:

```
docker run -d --rm --net=host \
  -v "$(pwd)"/out:/out \
  -e "INTERFACE=wlp3s0" \
  -e "FILTERS=and src 192.168.2.128 and dst net 142.250.0.0/16" \
  --name quic-capture fxbrit/spindump-docker
```

#### Compose

Docker Compose can make deployment easier by allowing to specify `ENV`
variables on file instead of entering complex commands. 
It also gives the option to create multiple pre-configurations that can be
run with a single command:

```
docker compose up -d <service_name>
```
