import sys
import re

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
            us = re.sub('us', '', line.split(":",1)[1])
            measure["rtt"] = float(str(int(us)/1000))
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
                "is_last": False
                }
        # New connection occured so measure might be flawed.
        elif "! The last" in line:
            measure["is_last"] = True
  filedata.close()
  return measures_list

'''
TODO: produce an indication of the accuracy, evaluate impact of is_last.
'''
def analyze_out(out):
    return

'''
Main function.
'''
def main(parser_out):
    for line in read(parser_out):
        print(line)

main(parser_out=sys.argv[1])
