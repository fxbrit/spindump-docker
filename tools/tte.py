import os
import re
import sys

'''
Read a parser.py output and extract valuable details.
'''
def read(filename):
  measures_list = []
  measure = {
    "interval": 0,
    "rtt": 0,
    "is_last": False,
    "deviation": 0
    }
  with open(filename, "r") as filedata:
      for line in filedata:
        line = re.sub(r"[\n\t]*", "", line)
        # Interval duration.
        if "lasted at most:" in line:
            ms = line.split(" = ",1)[1]
            measure["interval"] = float(re.sub('ms', '', ms))
        # Chromium internal RTT.
        elif "|||" in line:
            if "us" in line:
                us = re.sub('us', '', line.split(":",1)[1])
                measure["rtt"] = float(us)/1000
            elif "ms" in line:
                ms = re.sub('ms', '', line.split(":",1)[1])
                measure["rtt"] = float(ms)
        # Flip of the Spin Bit means dict is filled, except first iteration.
        elif "+++" in line and measure["interval"] != 0 and measure["rtt"] != 0:
            # deviation = [(acutal_value - expected_value) / expected_value] * 100
            # Only take 4 decimals and then covert to a float
            measure["deviation"] = float(
                "{:.4f}".format(
                    ((measure["interval"] - measure["rtt"]) / measure["rtt"])*100
                )
            )
            measures_list.append(measure)
            measure = {
                "interval": 0,
                "rtt": 0,
                "is_last": False,
                "deviation": 0
                }
        # New connection occured so measure might be flawed.
        elif "! The last" in line:
            measure["is_last"] = True
  filedata.close()
  return measures_list

'''
Produce an indication of the accuracy by means of average deviation.
Also evaluate the same metrics when excluding last interval and
obvious outliers.
'''
def analyze_out(measures_list):
    tot = tot_nolast = nolast = tot_pruned = not_pruned = 0
    entries = float(len(measures_list))
    for entry in measures_list:
        tot += entry["deviation"]
        if entry["is_last"] == False:
            tot_nolast += entry["deviation"]
            nolast += 1
        if entry["deviation"] < 100:
            tot_pruned += entry["deviation"]
            not_pruned += 1
    # Average deviation.
    avg = tot / entries
    # Average deviation excluding last interval of a connection.
    # avg_nolast = tot_nolast / float(nolast)
    # Average deviation excluding obvious outliers with more than 100% deviation
    avg_pruned = tot_pruned / float(not_pruned)
    pruned = entries - not_pruned
    # Percentage of pruned entries
    pruned_pct = float("{:.2f}".format(pruned*100/entries))
    out = "Average deviation: " + "{:.2f}".format(avg) + "%"
    if pruned_pct != 0.0:
        out += "\tPruned average deviation: " + "{:.2f}".format(avg_pruned) + "% - " + str(pruned_pct) + "% of the entries were pruned.\n"
    else:
        out += "\tNo pruning necessary.\n"
    return out

'''
Main function.
'''
def main(parser_out):
    for filename in os.listdir(parser_out):
        path = parser_out + "/" + filename
        out = analyze_out(read(path))
        print(out)

main(parser_out=sys.argv[1])
