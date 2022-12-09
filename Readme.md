To run create the source bind directory using:
```
mkdir sdmp-vol
```

Then eenter the following command:
```
docker run -p 127.0.0.1:443:443 --mount type=bind,source="$(pwd)"/sdmp-vol,target=/workdir --name port-capture -ti fxbrit/spindump
```

Or even:
```
docker run --net=host --mount type=bind,source="$(pwd)"/sdmp-vol,target=/workdir --name full-net-capture -ti fxbrit/spindump
```