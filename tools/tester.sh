#!/bin/bash

compose=name # Name of the Docker Compose config.
spindump_path=path/to/spindump-docker # The parent directory of tools.
chromium_path=path/to/chromium/src # The path to your Chromium checkout.
checkout=name # The name of your checkout containing QUIC client.
delay=100 # Delay introduced server side.
url=https://example.local # The URL to be fetched by QUIC client.
repeat_per_capture=1 # Number of requests for each QUIC client fetch.
tot_captures=1 # Number of captures in this test.

# Start the Docker container for the capture and create output dir.
start_capture () {
  cd $spindump_path
  mkdir -p tools/tester_output_$delay
  docker compose up -d $compose
}

# Stop the capture and move the capture file:
#   $1 is capture number.
stop_capture_and_move_output () {
    cd $spindump_path
    docker compose stop $compose
    cp ./$compose/capture.json tools/tester_output_$delay/capture_$1.json
}

# Execute a fetch with QUIC client:
#   $1 is capture number.
quic_go_get_it () {
    cd $chromium_path
    ./out/$checkout/quic_client $url --quiet --num_requests=$repeat_per_capture > $spindump_path/tools/tester_output/log_$1.txt 2>&1
}

for (( i=1 ; i<=$tot_captures ; i++ )); 
do
    echo "Starting capture number $i..."
    start_capture
    echo "QUIC client doing its thing..."
    quic_go_get_it $i
    echo "Stopping and saving the capture..."
    stop_capture_and_move_output $i
    echo "Finished capture number $i." 
done
