FROM ubuntu
RUN apt update\
    && apt upgrade -y\
    && apt install git pkg-config cmake make gcc libpcap-dev libncurses5-dev libcurl4-openssl-dev libmicrohttpd-dev -y
RUN mkdir workdir\
    && cd "$_"\
    && git clone https://github.com/EricssonResearch/spindump
RUN cd spindump\
    && cmake .\
    && make\
    && make install
WORKDIR /workdir/spindump
CMD spindump
