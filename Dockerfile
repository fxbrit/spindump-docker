FROM ubuntu
# select a network interface, if none is specified then use them all
ENV INTERFACE=any
# set a max number of packets to analyze, 0 means no limit
ENV MAX_RECEIVE=0
# filter by source or destination IP address or IP network
# by default take any
ENV SOURCE_IP=0.0.0.0/0
ENV DEST_IP=0.0.0.0/0
# fetch dependencies and create output directory
RUN apt-get update\
    && apt-get upgrade -y\
    && apt-get install git pkg-config cmake make gcc libpcap-dev libncurses5-dev libcurl4-openssl-dev libmicrohttpd-dev -y\
    && mkdir /out
# fetch spindump and build it
RUN git clone https://github.com/EricssonResearch/spindump\
    && cd spindump\
    && cmake .\
    && make\
    && make install
# capture QUIC traffic and save it in the output file
# also sets all the ENV variables
CMD spindump udp and port 443 --interface ${INTERFACE} --max-receive ${MAX_RECEIVE} --aggregate ${SOURCE_IP} ${DEST_IP} --textual --format json > /out/capture.json
