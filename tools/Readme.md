# Tools

A collection of tools to support [Spindump](https://github.com/EricssonResearch/spindump).

## Parser

Given a capture from the spindump-docker container, it produces a readable output with a summary of the Spin Bit flips. For example:

<img src="./img/parser.png" width=500>

## Tester

Bash scripts that automates QUIC client calls to a given URL and produces:
* a QUIC Client log file;
* a set of Spindump captures;
* the output of the Parser for each log - capture couple.

## tte

Time To Evaluate takes the Parser output and tries to understand the deviation that captures have from the internal RTT, and what impacts the results the most.

For its dependencies you can create a `venv` and then use:

```
python3 -m pip install -r requirements.txt
```
