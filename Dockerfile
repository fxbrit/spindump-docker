FROM ubuntu
# select a network interface, if none is specified then use them all
ENV INTERFACE=any
# set a max number of packets to analyze, 0 means no limit
ENV MAX_RECEIVE=0
# specify extra pcap filters in a tcpdump fashion
ENV FILTERS=
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
CMD spindump udp and port 443 ${FILTERS} --report-spins --interface ${INTERFACE} --max-receive ${MAX_RECEIVE} --textual --format json > /out/capture.json
