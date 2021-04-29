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

https://api.bls.gov/publicAPI/v2/timeseries/data/?&
catalog=true&startyear=2010&endyear=2014&calculations=true &annualaverage=true&aspects=true


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
    occ_selector = []
    for occ in soc_list:
        occ_name = occ["Occupation Name"] 
        occ_soc = occ["SOC Code"]
        occ_proj_growth = occ["Projected 10 Year Change"]
        occ_name_search = occ_name.lower().replace(" ","")
        occ_name_title = occ_name.title()
        occ_name_html = [occ_name_search, occ_name_title, occ_soc, occ_proj_growth]
        #occ_name_html = f"<option value='{occ_name_search}'>{occ_name.title()}</option>"
        occ_selector.append(occ_name_html)

    return occ_selector



def find_bls_data(job_soc):
    """
    Takes: A string. 6 Digit SOC code, formatted with no dash.
    Gives: a list of 
    """
    wage_response = requests.get("https://api.bls.gov/publicAPI/v2/timeseries/data/OEUS2600000000000"+job_soc+"08?registrationkey="+bls_secrets.api_key+"&latest=true")
    json_tst = wage_response.text
    wage_list = json.loads(json_tst)["Results"]["series"]
    median_wage = wage_list[0]['data'][0]['value']
    print(median_wage)

    emp_response = requests.get("https://api.bls.gov/publicAPI/v2/timeseries/data/OEUS2600000000000"+job_soc+"01?registrationkey="+bls_secrets.api_key+"&latest=true")
    json_tst2 = emp_response.text
    emp_list = json.loads(json_tst2)["Results"]["series"]
    current_emp = emp_list[0]['data'][0]['value']
    
    job_data = [current_emp, median_wage]
    BLS_CACHE[job_soc] = job_data

    return job_data


def search_postings(job_keyword):
    """
    I am a docstring and darn it I should be informative

    """
    indeed_response= requests.get('https://www.indeed.com/jobs?q='+ job_keyword +'&l=Ann+Arbor%2C+MI')
    soup = BeautifulSoup(indeed_response.text, 'html.parser')

    results_raw = soup.find('div', id="searchCountPages")
    results_number = str(results_raw).split()[5]
    POSTING_parent = soup.find('td', id='resultsCol')

    postings = POSTING_parent.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result')

    posting_fax = []
    your_available_openings_html = []

    for posting in postings:
        posting_job_title = posting.find('a', class_="jobtitle turnstileLink")
        test_posting_title = posting_job_title["title"]
        test_posting_employer = posting.find('span', class_="company").text.strip()
        test_posting_str = f"{test_posting_title} for {test_posting_employer}"
        your_available_openings_html.append(test_posting_str)

    posting_fax = [results_number, your_available_openings_html]

    return posting_fax


def graph_wage(occupation, query_result_wage): 
    """
    I am a docstring and darn it I should be informative
    """
    wages = [19.67, query_result_wage]
    jobs_to_compare = ["Michigan Median", occupation]
    bar_data = go.Bar(x=jobs_to_compare, y=wages)
    basic_layout = go.Layout(title="Hourly Earnings for Your Selected Job Compared to the State Median")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    #fig.show()
    return fig


in_demand = save_in_demand_jobs()
options = make_list_of_occ_choices(in_demand)
occ_dict = {}
for occ in options:
    occ_dict[occ[0]] = [occ[1], occ[2], occ[3]]
#print(occ_dict)
SOC_CACHE = save_in_demand_jobs()
#print(SOC_CACHE)

@app.route('/')
def index(): 
    return render_template('occupation_choice_page.html', list_of_occ_choices=options)


@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    your_occupation = request.form["occupations"]
    nice_name = occ_dict[your_occupation][0]
    search_name=nice_name.replace(" ","+")
    growth = occ_dict[your_occupation][2]
    bls_result = find_bls_data(occ_dict[your_occupation][1])
    emp_graph = bls_result[0]
    wage_graph = graph_wage(nice_name, bls_result[1])
    div=wage_graph.to_html(full_html=False)
    postings_search = search_postings(search_name)
    postings_list = postings_search[1]
    total_postings = postings_search[0]
    return render_template('occupation_results.html', 
        your_occupation=nice_name, decade_projection=growth, current_emp=emp_graph, plot_div_2=div, results_count=total_postings, results_list=postings_list)


if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    #in_demand = save_in_demand_jobs()
    #options = make_list_of_occ_choices(in_demand)
    app.run(debug=True)
