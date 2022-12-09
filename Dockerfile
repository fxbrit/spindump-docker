FROM ubuntu
RUN apt-get update\
    && apt-get upgrade -y\
    && apt-get install git pkg-config cmake make gcc libpcap-dev libncurses5-dev libcurl4-openssl-dev libmicrohttpd-dev -y\
    && mkdir /out
RUN git clone https://github.com/EricssonResearch/spindump\
    && cd spindump\
    && cmake .\
    && make\
    && make install
CMD spindump udp and port 443 --textual --format json > /out/capture.json
