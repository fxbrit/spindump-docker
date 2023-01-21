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
  spins.sort(key=itemgetter("dest_ipaddr", "timestamp"))
  for spin in spins:
    if dest_ip != spin["dest_ipaddr"]:
      dest_ip = spin["dest_ipaddr"]
      out += "Destination IP address: " + str(dest_ip) + "\n"
    if conn_id != spin["connection_id"]:
      conn_id = spin["connection_id"]
      out += "\tConnection ID: " + str(conn_id) + "\n"
    # Spindump timestamps are in µs, we must convert to s
    timestamp = datetime.fromtimestamp(spin["timestamp"] / (10.0**6))
    out += ("\t" + timestamp.strftime("%H:%M:%S.%f") + 
            " Spin Bit: " + str(spin["spin_bit"]) + "\n")
  return out

# Write to file the output of parse_file()
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
