#################################
##### Name: Karley Thurston
##### Uniqname: thurstkd
#################################

"""
Welcome! This program allows you to select an occupation to view its current and projected employment, median wage, and current Ann Arbor Job Postings. 

Just select from the list of common occupations to get started. 

"""



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
Michigan type code: S
Michigan area code: 260000000
Industry code: optional 6 dig naics; 000000 for all
Occupation: 6 digit SOC
Last 2 digits: 
data_type_code	data_type_text
01	Employment
08	Hourly median wage


 """                   

 
import json, requests, csv
from bs4 import BeautifulSoup
import bls_secrets
import plotly
import plotly.graph_objects as go 
from flask import Flask, render_template, request
SOC_CACHE = None
BLS_CACHE = {}
INDEED_CACHE = {}
app = Flask(__name__)



def save_in_demand_jobs():
    with open('job_finder_seed_codes.csv', mode='r', newline='', encoding='utf-8-sig') as file_obj:
            data = list(csv.DictReader(file_obj))

    SOC_CACHE = data
    return SOC_CACHE

def make_list_of_occ_choices(soc_list):
    """
    Takes list of dictionaries (SOC_CACHE) and makes them into an html-formatted string to be used as choices in flask app.
    """
    occ_selector = ""
    for occ in soc_list:
        occ_name = occ["Occupation Name"] 
        occ_name_search = occ_name.lower().replace(" ","")
        occ_name_html = f"<option value='{occ_name_search}'>{occ_name.title()}</option>"
        occ_selector=occ_selector+occ_name_html

    return occ_selector

def find_bls_data(job_keyword):
    """
    I am a docstring and darn it I should be informative
    """
    response = requests.get("https://api.bls.gov/publicAPI/v2/timeseries/data/LAUCN040010000000005?registrationkey="+bls_secrets.api_key+"&latest=true")
    json_tst = response.text
    emp = json.loads(json_tst)["Results"]["series"]
    print(emp[0]['data'])


    BLS_CACHE['test'] = emp[0]['data']

    print(BLS_CACHE)
    return emp

def graph_employment(emp_by_year): 
    """
    I am a docstring and darn it I should be informative
    """
    emp_by_year = []
    years = []
    basic_layout = go.Layout(title="Projected Employment for Your Selected Occupation")
    fig = go.Figure(data=go.Scatter(x=years, y=emp_by_year), layout=basic_layout)
    return fig

"""
INDEED_BASE_URL = 'https://www.indeed.com/jobs?q=&l=Ann+Arbor%2C+MI'

keyword = input
"""

def search_postings(job_keyword):
    """
    I am a docstring and darn it I should be informative
    You promised the total number of active postings and titles/ employers of first page results
    """
    indeed_response= requests.get('https://www.indeed.com/jobs?q='+ job_keyword +'&l=Ann+Arbor%2C+MI')
    soup = BeautifulSoup(indeed_response.text, 'html.parser')

    results_number = soup.find('div', id="searchCountPages")
    print(results_number)
    POSTING_parent = soup.find('td', id='resultsCol')

    postings = POSTING_parent.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result')
    test_posting_title = None
    test_posting_employer = None
    your_available_openings_html = ""
    #your_available_openings_list = []

    for posting in postings:
        job_tag = posting.find('a')
        test_posting_title = job_tag['title']
        test_posting_employer = posting.find('span', class_="company").text.strip()
    #make an allowance for missing employers
        test_posting_str = f"{test_posting_title} for {test_posting_employer}<br/>"
    #    your_available_openings_list.append(test_posting_str)
        your_available_openings_html=your_available_openings_html+test_posting_str

    INDEED_CACHE[job_keyword] = your_available_openings_html
    #print(INDEED_CACHE)
    return your_available_openings_html
"""
file1 = open("SoupPretty.txt", "a")
#a = append only; w = write only and would keep overwriting
file1.write(soup.prettify())
file1.close()
"""
a2_median = None


def graph_wage(occupation, query_result_wage): 
    """
    I am a docstring and darn it I should be informative
    """
    wages = [19.67, query_result_wage]
    jobs_to_compare = ["Ann Arbor Median", occupation]
    bar_data = go.Bar(x=wages, y=jobs_to_compare)
    basic_layout = go.Layout(title="Wages for Your Selected Job Compared to the Local Median")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    return fig




@app.route('/')
def index():     
    in_demand = save_in_demand_jobs()
    options = make_list_of_occ_choices(in_demand)
    return render_template('occupation_choice_page.html', list_of_occ_choices=options)


@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    your_occupation = request.form["occupations"]
    bls_result = find_bls_data(your_occupation)
    emp_graph = graph_employment(bls_result)
    wage_graph = graph_wage(your_occupation, bls_result)
    postings_list = search_postings(your_occupation)
    return render_template('occupation_results.html', 
        your_occupation=your_occupation, plot_div_1=emp_graph, plot_div_2=wage_graph, results_list=postings_list)

if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)
