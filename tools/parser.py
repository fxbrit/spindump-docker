import json
from datetime import datetime
from operator import itemgetter

# Convert a Spindump capture into a proper JSON and return the filename.
def fix_file(filename):
  new_filename = filename.split(".", 1)[0] + "_fixed.json"
  with open(filename) as in_file:
    file_data = in_file.read()
    # Normalize the 'Addrs' field of the Spindump capture.
    file_data = file_data.replace('["', '"[').replace('"]', ']"').replace('","', ',')
  # Add closing character.
  file_data += "\n]"
  with open(new_filename, "w") as out_file:
    out_file.write(file_data)
  return new_filename 

# Take a JSON containing a Spindump capture and print the Spin Bit
# value of each connection at different timestamps.
def parse_file(filename):
  spins = []
  dest_ip = ""
  conn_id = "" 
  out = ""
  with open(filename) as to_parse:
    for entry in json.load(to_parse):
      if entry["Event"] == "spinvalue":
        spin = {"dest_ipaddr" : entry["Addrs"].split(",", 1)[1].split("]", 1)[0],
                "connection_id" : entry["Session"].split("-", 1)[1].split(" ", 1)[0],
                "timestamp" : entry["Ts"],
                "spin_bit" : entry["Value"]}
        spins.append(spin)
  # Each connection has its own Spin Bit value so we should divide
  # by destination IP address first, and then sort by timestamp.
  spins.sort(key=itemgetter("dest_ipaddr", "connection_id", "timestamp"))
  for spin in spins:
    if dest_ip != spin["dest_ipaddr"]:
      dest_ip = spin["dest_ipaddr"]
      out += "\nDestination IP address: " + str(dest_ip) + "\n"
      current_spin, flip_counter, start_timestamp = (0,0,None)
    if conn_id != spin["connection_id"]:
      conn_id = spin["connection_id"]
      # Spindump parses new Connection IDs only on Long Headers. For Short Headers
      # it uses UDP, IP-IP, port-port instead: this means a new Connection ID is a new
      # connection towards the same IP address.
      out += "\tConnection ID: " + str(conn_id) + ", new connection towards " + str(dest_ip) + "\n"
      # As a result we want to start counting flips from 0.
      current_spin, flip_counter, start_timestamp = (0,0,None)
    # Spindump timestamps are in µs, we must convert to s.
    timestamp = datetime.fromtimestamp(spin["timestamp"] / (10.0**6))
    spin_bit = spin["spin_bit"]
    if current_spin != spin_bit:
      if start_timestamp is None:
        current_spin = spin_bit
        start_timestamp = timestamp
        flip_counter+=1
        previous = timestamp
        out += "\t--- Flip number: " + str(flip_counter) + "\n"
      else:
        if (previous <= start_timestamp):
          out += "\t--- Single packet in this marking interval\n"
        else:
          interval = previous - start_timestamp
          interval_s = interval.seconds
          interval_ms = interval.microseconds * (10.0**-3)
          out += ("\t--- Marking interval lasted at least: " +
                  previous.strftime("%H:%M:%S.%f") +
                  " - " +
                  start_timestamp.strftime("%H:%M:%S.%f") +
                  " = " +
                  str(interval_s) + ":" + str(interval_ms) + "ms\n")
        time_passed = timestamp - start_timestamp
        time_passed_s = time.seconds
        time_passed_ms = time_passed.microseconds * (10.0**-3)
        # This statement can be used to debug and filter out small
        # time intervals that might represent fuzzy edges.
        if (ms >= 0):
          out += ("\t--- Marking interval lasted at most: " +
                  timestamp.strftime("%H:%M:%S.%f") +
                  " - " +
                  start_timestamp.strftime("%H:%M:%S.%f") +
                  " = " +
                  str(time_passed_s) + ":" + str(time_passed_ms) + "\n")
          current_spin = spin_bit
          start_timestamp = timestamp
          flip_counter+=1
          out += "\t--- Flip number: " + str(flip_counter) + "\n"
    else:
      previous = timestamp
    out += ("\t" + timestamp.strftime("%H:%M:%S.%f") + 
            " Spin Bit: " + str(spin["spin_bit"]) + "\n")
  return out

# Write to file the output of parse_file().
def write_output(output):
  with open("parser_out.txt", "w") as out_file:
    out_file.write(output)

def main():    
  filename = input("Name of the capture file: ")
  # filename = "capture.json"
  to_parse = fix_file(filename)
  parsed = parse_file(to_parse)
  write_output(parsed)

main()
