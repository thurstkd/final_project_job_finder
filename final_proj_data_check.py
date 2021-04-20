"""
HTTP Type: 	GET
URL (JSON): 	https://api.bls.gov/publicAPI/v2/timeseries/data/
URL for Excel output: 	https://api.bls.gov/publicAPI/v2/timeseries/data/.xlsx
Payload: 	series_id
Example Payload: LAUCN040010000000005

https://api.bls.gov/publicAPI/v2/timeseries/data/?&
catalog=true&startyear=2010&endyear=2014&calculations=true &annualaverage=true&aspects=true

Key to Occupational Employment and Wage Statistics Data:
OE: data prefixx
Ann Arbor area type code: M
Ann Arbor area code: 0011460
Industry code: optional 6 dig naics; 000000 for all
Occupation: 6 digit SOC
Last 2 digits: 
data_type_code	data_type_text
01	Employment
02	Employment percent relative standard error
03	Hourly mean wage
04	Annual mean wage
05	Wage percent relative standard error
06	Hourly 10th percentile wage
07	Hourly 25th percentile wage
08	Hourly median wage
09	Hourly 75th percentile wage
10	Hourly 90th percentile wage
11	Annual 10th percentile wage
12	Annual 25th percentile wage
13	Annual median wage
14	Annual 75th percentile wage
15	Annual 90th percentile wage
16	Employment per 1,000 jobs
17	Location Quotient

 """                   

 
import json, requests
from bs4 import BeautifulSoup
import bls_secrets
BLS_CACHE = {}
INDEED_CACHE = {}


response = requests.get("https://api.bls.gov/publicAPI/v2/timeseries/data/LAUCN040010000000005?registrationkey="+bls_secrets.api_key+"&latest=true")
json_tst = response.text
emp = json.loads(json_tst)["Results"]["series"]
print(emp[0]['data'])


BLS_CACHE['test'] = emp[0]['data']

print(BLS_CACHE)

"""
INDEED_BASE_URL = 'https://www.indeed.com/jobs?q=&l=Ann+Arbor%2C+MI'

keyword = input
"""

keyword = 'welder'
indeed_response= requests.get('https://www.indeed.com/jobs?q='+ keyword +'&l=Ann+Arbor%2C+MI')
soup = BeautifulSoup(indeed_response.text, 'html.parser')

results_number = soup.find('div', id="searchCountPages")
print(results_number)
POSTING_parent = soup.find('td', id='resultsCol')
#print(POSTING_parent)

postings = POSTING_parent.find_all('div', class_='jobsearch-SerpJobCard')
test_posting = postings[0]
#for posting in postings:
#    job_tag = posting.find('a')
#    print(job_tag['title'])

INDEED_CACHE[keyword] = test_posting
print(INDEED_CACHE)
"""
file1 = open("SoupPretty.txt", "a")
#a = append only; w = write only and would keep overwriting
file1.write(soup.prettify())
file1.close()
"""