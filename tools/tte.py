import os
import re
import sys
from texttable import Texttable

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
        # Chromium internal RTT or netem delay.
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
                    abs(((measure["interval"] - measure["rtt"]) / measure["rtt"]))*100
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
def analyze_out(measures_list, t):
    tot = rtt = 0
    nolast = tot_nolast = rtt_nolast = 0
    tot_pruned = not_pruned = rtt_pruned = 0
    entries = float(len(measures_list))
    row = []
    for entry in measures_list:
        tot += entry["deviation"]
        rtt += entry["rtt"]
        if entry["is_last"] == False:
            tot_nolast += entry["deviation"]
            nolast += 1
            rtt_nolast += entry["rtt"]
        if entry["deviation"] < 100:
            tot_pruned += entry["deviation"]
            not_pruned += 1
            rtt_pruned += entry["rtt"]
    # If no valid measurements.
    if entries == 0:
        t.add_row(["","","","","","","",""])
        return t
    # Average deviation.
    avg = tot / entries
    # Average deviation excluding last interval of a connection.
    # avg_nolast = tot_nolast / float(nolast)
    # Average deviation excluding obvious outliers with more than 100% deviation
    if not_pruned != 0:
        avg_pruned = tot_pruned / float(not_pruned)
    else:
        # In case all entries have been pruned.
        avg_pruned = None
    pruned = entries - not_pruned
    # Percentage of pruned entries
    pruned_pct = float("{:.2f}".format(pruned*100/entries))
    # AVG RTT
    avg_rtt = rtt / entries
    row.append("{:.3f}".format(avg_rtt))
    # AVG Deviation (% and ms)
    row.append("{:.3f}".format(avg))
    row.append("{:.3f}".format(avg * avg_rtt / 100))
    if pruned_pct != 0.0:
        if avg_pruned == None:
            row.append("-")
            row.append("-")
        else:
            # AVG Deviation with pruned outliers (% and ms)
            row.append("{:.3f}".format(avg_pruned))
            row.append("{:.3f}".format(avg_pruned * avg_rtt / 100))
        # Percentage and number of pruned entries
        row.append(pruned_pct)
        row.append(int(pruned))
    else:
        row.append("")
        row.append("")
        row.append("")
        row.append("None")
    row.append(int(entries))
    t.add_row(row)
    return t

'''
Main function.
'''
def main(parser_out):
    table = Texttable()
    table.header(
        [
        "AVG RTT (ms)",
        "AVG Deviation (%)",
        "AVG Deviation (ms)",
        "Pruned AVG Dev. (%)",
        "Pruned AVG Dev. (ms)",
        "Pruned (%)",
        "Pruned (#)",
        "Total (#)"
        ]
    )
    table.set_cols_width([15,20,20,20,20,20,10,10])
    for filename in os.listdir(parser_out):
        path = parser_out + "/" + filename
        measures_list = read(path)
        table = analyze_out(measures_list, table)
    print(table.draw())

main(parser_out=sys.argv[1])
