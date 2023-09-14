# nrdscan
Scans newly registered domains (NRD) for a given list of reference domains using direct and fuzzy string matching. Get ahead of those evil phishers now! ;)

The script uses the lists availabe at https://whoisds.com/newly-registered-domains. The site states that:

*The data provided below is daily list of Newly Registered Domains without whois database downloaded free of charge; except where otherwise stated, they may be reused, including for commercial purposes, without a license and without any payment.*

So it is free, but updated only every day. Therefore you might be 24 hours or more behind once you find out that there's a NRD relevant to you.


## Usage
```
usage: nrdscan.py [-h] -i INPUTFILE [-o OUTPUTFILE] [-fr FUZZRATIO] [-c]

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputfile INPUTFILE
                        file containing a list of domain names. one name per line.
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        file to write the result to. default is to print to stdout.
  -fr FUZZRATIO, --fuzzratio FUZZRATIO
                        ratio to use for fuzzy string matching. default is 75. NOTE: set to 0 to disable fuzzy matching.
  -c, --clean           clean working directories after execution. default is to leave the downloaded domain lists.
```
## Examples

```
nrdscan.py -i mydomainlist.txt -o myoutputfile.csv -fr 85 -c
```
The command above reads a list of domains from the file `mydomainlist.txt` and outputs the results into a CSV-file called `myoutputfile.csv`. A distance of `85` is used for fuzzy matching (default is 75), so this usually means less false-positives but also maybe no match if the malicious NRD deviates more from the original domain.
Finally the switch `-c` tells the script to clean up (aka delete) the full domain lists downloaded during execution.
