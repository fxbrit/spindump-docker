import json
import os
import sys
from datetime import datetime
from operator import itemgetter

'''
Convert a Spindump capture into a proper JSON and return the filename.
'''
def fix_file(filename):
  new_filename = "fixed.json"
  with open(filename) as in_file:
    file_data = in_file.read()
    # Normalize the 'Addrs' field of the Spindump capture.
    file_data = file_data.replace('["', '"[').replace('"]', ']"').replace('","', ',')
  # Add closing character.
  file_data += "\n]"
  with open(new_filename, "w") as out_file:
    out_file.write(file_data)
  return new_filename 

'''
Take a JSON containing a Spindump capture and print the Spin Bit
value of each connection at different timestamps.
'''
def parse_file(filename, log_out):
  spins = []
  dest_ip = out = conn_id = ""
  log_line = flip_counter = 0
  with open(filename) as to_parse:
    for entry in json.load(to_parse):
      if entry["Event"] == "spinvalue":
        spins.append(parse_entry(entry))
  # Each connection has its own Spin Bit value so we should divide
  # by destination IP address first, and then sort by timestamp.
  spins.sort(key=itemgetter("dest_ipaddr", "timestamp", "connection_id"))
  for i, spin in enumerate(spins):
    if dest_ip != spin["dest_ipaddr"]:
      dest_ip = spin["dest_ipaddr"]
      out += "\nDestination IP address: " + str(dest_ip) + "\n"
      # The rest of the changes needed by an IP change are addressed by the inevitable
      # change of Connection ID.
    if conn_id != spin["connection_id"]:
      conn_id = spin["connection_id"]
      # Spindump parses new Connection IDs only on Long Headers. For Short Headers
      # it uses UDP, IP-IP, port-port instead: this means a new Connection ID is a new
      # connection towards the same IP address. As a result we want to start counting
      # flips from 0.
      new_conn = True
    else:
      new_conn = False
    # Spindump timestamps are in µs, we must convert to s.
    timestamp = datetime.fromtimestamp(spin["timestamp"] / (10.0**6))
    spin_bit = spin["spin_bit"]
    # First iteration does not need to do much.
    if i == 0:
      current_spin = spin_bit
      start_timestamp = timestamp
      flip_counter+=1
      previous = timestamp
      out += "\tConnection ID: " + str(conn_id) + ", new connection towards " + str(dest_ip) + "\n"
      out += print_flip(flip_counter)
    else:
      # Same Connection ID but different value of the Spin Bit
      # or Change of Connection ID
      if new_conn or current_spin != spin_bit:
        dict = compute_intervals(previous, start_timestamp, timestamp)
        out += dict["out"]
        current_spin = spin_bit
        start_timestamp = timestamp
        if (dict["go_on"]):
          out += log_out[log_line]
          log_line+=1
          if (new_conn):
            flip_counter, new_conn = (0,False)
            out += "\tConnection ID: " + str(conn_id) + ", new connection towards " + str(dest_ip) + "\n"
            # When a new connection occurs the previous one is terminated so a lack of marked packets
            # in between the two might impact the connection. The new handshake also takes place in
            # between, further impacting the result.
            out += "\t! The last measurement of the past connection might be impacted by a lack of packets\n"
          flip_counter+=1
          out += print_flip(flip_counter)
      else:
        previous = timestamp
    # The timestamp and the Spin Bit should always be printed.
    out += ("\t" + timestamp.strftime("%H:%M:%S.%f") + 
            " Spin Bit: " + str(spin_bit) + "\n")
    # For the last measurement available we can only estimate a duration
    # of the marking interval. This is NOT a valid Spin Bit measurement
    # since no further flip occurs and no other packets are sent.
    if i == (len(spins) - 1):
      interval = previous - start_timestamp
      interval_s = interval.seconds
      interval_ms = interval.microseconds * (10.0**-3)
      out += ("\t--- Last marking interval lasted at least:\t" +
              previous.strftime("%H:%M:%S.%f") +
              " - " +
              start_timestamp.strftime("%H:%M:%S.%f") +
              " = " +
              str(interval_s*1000 + interval_ms) + "ms\n")
      out += "\t! This is not a valid Spin Bit measurement since no further flip or packet exists\n"
  return out

'''
Returns an ouput string for Spin Bit flip.
'''
def print_flip(flip_counter):
  return "\t+++ Flip number: " + str(flip_counter) + "\n"

'''
Given an entry in the capture return a dictionary containing the relevant
Spin Bit metrics.
'''
def parse_entry(entry):
  return {"dest_ipaddr" : entry["Addrs"].split(",", 1)[1].split("]", 1)[0],
          "connection_id" : entry["Session"].split("-", 1)[1].split(" ", 1)[0],
          "timestamp" : entry["Ts"],
          "spin_bit" : entry["Value"]}

'''
Function that computes the marking intervals and decides how
the rest of the computation should go on according to its result.
'''
def compute_intervals(previous, start_timestamp, timestamp):
  go_on = False
  if (previous <= start_timestamp):
    out = "\t--- Single packet in this marking interval\n"
  else:
    interval = previous - start_timestamp
    interval_s = interval.seconds
    interval_ms = interval.microseconds * (10.0**-3)
    out = ("\t--- Marking interval lasted at least:\t" +
            previous.strftime("%H:%M:%S.%f") +
            " - " +
            start_timestamp.strftime("%H:%M:%S.%f") +
            " = " +
            str(interval_s*1000 + interval_ms) + "ms\n")
  time_passed = timestamp - start_timestamp
  time_passed_s = time_passed.seconds
  time_passed_ms = time_passed.microseconds * (10.0**-3)
  # This statement can be used to debug and filter out small
  # time intervals that might represent fuzzy edges.
  if (time_passed_ms >= 0):
    out += ("\t--- Marking interval lasted at most:\t" +
            timestamp.strftime("%H:%M:%S.%f") +
            " - " +
            start_timestamp.strftime("%H:%M:%S.%f") +
            " = " +
            str(time_passed_s*1000 + time_passed_ms) + "ms\n")
    go_on = True
  return {"out": out, "go_on": go_on}

'''
Write to file the output of parse_file().
'''
def write_output(output):
  with open("parser_out.txt", "w") as out_file:
    out_file.write(output)

'''
Read a Chromium log file to get internal RTT values.
'''
def read_log(filename):
  out = []
  with open(filename, "r") as filedata:
      for line in filedata:
          sample = "Measured latest_rtt_ is"
          if sample in line:
              us = line.rstrip('\n').split("is: ",1)[1]
              out.append("\t||| Internal RTT in Chromium:\t" + us + "\n")
  filedata.close()
  return out

'''
Main function.
'''
def main(capture, log):    
  to_parse = fix_file(capture)
  log_out = read_log(log)
  parsed = parse_file(to_parse, log_out)
  os.remove(to_parse)
  write_output(parsed)

main(capture=sys.argv[1], log=sys.argv[2])
