import csv, re, argparse
import urllib.request as req
import xml.etree.ElementTree as ET
#input must be arrays
def addTerms(base, keys, values):
    for i, k in enumerate(keys):
        base = addTerm(base, k, values[i])
    return base

def addTerm(base, key, value):
    return base + key + "=" + value + "&"

dbKey = "db";
authorIdTerm = "[Author]"
db = "pubmed"
baseUrl = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
baseUrl = addTerm(baseUrl, dbKey, db)
pattern = re.compile('[\W]+')

parser = argparse.ArgumentParser(description="process the given csv, searching pubmed for publications by the listed authors")
parser.add_argument('inputfilename', type=str, help='file name of input csv to be processed')
parser.add_argument('outputfilename', type=str, help='file name of output csv, must be different from input')

args = parser.parse_args()

cntFieldName = 'Total Publications'

with open(args.inputfilename) as ss, open(args.outputfilename, 'wt') as ssWrite:
    ssReader = csv.DictReader(ss)
    print(ssReader.fieldnames)
    fieldNames = ssReader.fieldnames
    fieldNames.append(cntFieldName)
    ssWriter = csv.DictWriter(ssWrite, fieldNames)
    ssWriter.writeheader()
    counts = list()
    for row in ssReader:
        fieldnames = row.keys()
        lname= pattern.sub(' ', row['LastName'])
        fname = pattern.sub(' ', row['FirstName'])
        mi = pattern.sub(' ', row['MiddleInitial'])
        if(len(mi)!=0): authorTerm = lname+',+'+fname+'+'+mi+authorIdTerm
        else: authorTerm = lname+',+'+fname+authorIdTerm
        authorTerm = '+'.join(re.split(' ', authorTerm))
        url = addTerm(baseUrl, "term", authorTerm)
        print('GET: ' +url)
        with req.urlopen(url) as resp:
            respString = resp.read().decode('UTF-8')
            #print(respString)
            root = ET.fromstring(respString)
            errorList = root.find('.//ErrorList')
            if(errorList is not None):
                #was an error. report 0 as count
                for child in errorList:
                    print('got ERROR: resp tag was' + child.tag)
                count = 0
            field = root.find('.//Field')
            if(field is not None):
                if(root.find('.//Field').text != 'Full Author Name'):
                    fieldText = root.find('.//Field').text
                    print("error in response from: " + url + " Site didn't interpret query as Author full name. instead was: " + fieldText)
                    count = 0
                else:
                    count = str(root.find('.//Count').text)
        print("count: " + str(count))
        row[cntFieldName] = count
        ssWriter.writerow(row)
