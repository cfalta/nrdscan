import argparse
from datetime import datetime, timedelta
import base64
import requests
from zipfile import ZipFile
import os
from thefuzz import fuzz
import csv

class DomainMatch:
    def __init__(self, domain, newdomain, matchtype, ratio):
        self.domain = domain
        self.newdomain = newdomain
        self.matchtype = matchtype
        self.ratio = ratio

    def __iter__(self):
        return iter([self.domain, self.newdomain, self.matchtype, self.ratio])

def getDomainListFromFile(filename):
    with open(filename) as f:
        content = f.readlines()
    return [x.strip() for x in content]


argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--inputfile", help="file containing a list of domain names. one name per line.",type=str, required=True)
argParser.add_argument("-o", "--outputfile", help="file to write the result to. default is to print to stdout.",type=str)
argParser.add_argument("-fr", "--fuzzratio", help="ratio to use for fuzzy string matching. default is 75. NOTE: set to 0 to disable fuzzy matching.",type=int, default=75)
argParser.add_argument('-c', "--clean", help="clean working directories after execution. default is to leave the downloaded domain lists.", action='store_true')

args = argParser.parse_args()

yesterdayAsTimeStamp = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
workingdirectory = os.path.join(os.getcwd(), yesterdayAsTimeStamp)

if os.path.exists(workingdirectory):
    print("Directory " + workingdirectory + " already exists. Aborting.")
else:
    os.makedirs(workingdirectory)

    # download a list of new domains from https://whoisds.com/newly-registered-domains
    # and save it to a file called "newdomains.txt"

    baseurl = "https://www.whoisds.com//whois-database/newly-registered-domains/"
    baseurlsuffix = "/nrd"
    filename = yesterdayAsTimeStamp + ".zip"
    filenameb64 = (base64.b64encode(filename.encode('ascii'))).decode('ascii')

    downloadurl = baseurl + filenameb64 + baseurlsuffix
    downloadfilename = os.path.join(workingdirectory, filename)

    print("Downloading " + downloadurl + " to " + downloadfilename)
    r = requests.get(downloadurl, allow_redirects=True)

    with open(downloadfilename, 'wb') as f:
        f.write(r.content)

    # unzip the file
    with ZipFile(downloadfilename, 'r') as zip_ref:
        zip_ref.extractall(workingdirectory)

    # set the input files for domain matching
    newdomainfile = os.path.join(workingdirectory,"domain-names.txt")
    newdomains = getDomainListFromFile(newdomainfile)
    mydomains = getDomainListFromFile(args.inputfile)

    # set result array
    result = []

    # for every domain in the reference set, check if it is contained in the new domains by
    for mydomain in mydomains:
        # 1. get the domain (ignore the TLD) - we assume that the first part is the string you're looking for (e.g. domainname.tld or domainname.co.tld)
        domain = mydomain.split(".")[0]
        # 2. walk through every item in the new domain list
        for newdomain in newdomains:
            # 3. check for direct matches (e.g. newspaper.com matches mynewspaper.com because the string "newspaper" is in there as a whole)
            if domain in newdomain:
                result.append(DomainMatch(mydomain, newdomain, "DirectMatch", 0))
                #result.append("DirectMatch: " + domain + " in " + newdomain)
            # 4. check for fuzzy matches if theres no direct match (e.g. newspaper.com matches news-paper.com due to the distance limit)
            elif args.fuzzratio > 0:
                newdomainpart = newdomain.split(".")[0]
                fuzzyratio = fuzz.ratio(domain, newdomainpart)
                if fuzzyratio >= args.fuzzratio:
                    #result.append("FuzzyMatch: " + domain + " in " + newdomain + " (ratio: " + str(fuzzyratio) + ")")
                    result.append(DomainMatch(mydomain, newdomain, "FuzzyMatch", fuzzyratio))


    if result:
        # print the result summary
        print("Found " + str(len(result)) + " new domains matching " + str(len(mydomains)) + " domains in your reference set:")
        
        #print header first
        print("{:20} {:20} {:20} {:20}".format("Domain", "NewDomain", "MatchType", "Ratio"))
        print("---------------------------------------------------------------------------------------------------")   
        for domain in result:
            print("{:20} {:20} {:20} {:20}".format(domain.domain, domain.newdomain, domain.matchtype, domain.ratio))
    else:
        print("No matches found.")

    # if the result should be written to a file, first check if the file exists and write the csv header if it does not
    if args.outputfile and not os.path.exists(args.outputfile):
        with open(args.outputfile, 'a') as f:
            writer=csv.writer(f, delimiter=',',lineterminator='\n')
            writer.writerow(["Domain", "NewDomain", "MatchType", "Ratio"])
    
    # then write the result to the file, again making sure it exists
    if args.outputfile:
        with open(args.outputfile, 'a') as f:
            writer=csv.writer(f, delimiter=',',lineterminator='\n')
            for item in result:
                writer.writerow(item)

    # clean up
    if args.clean:
        os.remove(downloadfilename)
        os.remove(newdomainfile)
        os.rmdir(workingdirectory)