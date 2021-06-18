import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt 
from pytrends.request import TrendReq
from datetime import datetime
import pytz
from pytz import timezone 
import seaborn as sns


def suggestions(keyword, pytrend):
    df = pd.DataFrame(pytrend.suggestions(keyword))
    d = df[['mid', 'title']]
    new_d = d.set_index('mid')
    return new_d.to_dict()['title']
def related_queries(keyword, spec, correct_format, pytrend):
    pytrend.build_payload([keyword], cat=0, timeframe=correct_format, geo='', gprop='')    
    related_queries = pytrend.related_queries()
    return related_queries[keyword][spec]


# sidebar 
st.sidebar.write("## Trend based on keyword")
keyword = st.sidebar.text_input("Enter a keyword", help= "Look up on Google Trends")
related_terms = st.sidebar.selectbox("Select which terms you would like to see",['suggested terms', 'top related queries', 'rising related queries'])
time_range = st.sidebar.selectbox("Select a time range you are interested in", ['5 years', '1 year', '1 month','3 months', '1 day', '7 days', '1 hour', '4 hours' ])
pytrend = TrendReq(hl = 'en US', tz = 300)

if keyword and related_terms and time_range:
    sns.set(color_codes=True)

    options = ['today 5-y', 'today 12-m','today 1-m', 'today 3-m','now 1-d', 'now 7-d', 'now 1-H', 'now 4-H']
    theoptions = ['5 years', '1 year', '1 month','3 months', '1 day', '7 days', '1 hour', '4 hours' ]

    ind = theoptions.index(time_range)
    correct_format = options[ind]
    
    sug = list()
    percent_inc = None
    if related_terms == 'suggested terms':
        sug = [keyword] + list(suggestions(keyword, pytrend).values())
    elif related_terms == 'top related queries':
        sug = related_queries(keyword, 'top', correct_format, pytrend)[0:10]['query'].to_list()
    elif related_terms == 'rising related queries':
        rising = related_queries(keyword, 'rising', correct_format, pytrend)
        percent_inc = rising.set_index('query').to_dict()['value']
        sug = rising[0:10]['query'].to_list()
    
    colors = ['b','g','r','c','m','y','purple','gray','k','b']
    looked_at = []

    for word in range(len(sug)):
        if sug[word].lower() in looked_at or len(sug[word].split()) > 10:
            continue
        looked_at.append(sug[word].lower())
        pytrend.build_payload([sug[word]], cat=0, timeframe=correct_format, geo='', gprop='')
        df = pytrend.interest_over_time()
        df.drop(columns=['isPartial'], inplace=True)
        index = df.index
        est = timezone('US/Eastern')
        df.index = index.tz_localize(pytz.utc).tz_convert(est)
        fig, ax = plt.subplots()
        ax = df[sug[word]].plot.line(color = colors[word])
        ax.legend(loc = 'upper right', bbox_to_anchor=(1.0, 1), prop = {'size':10})
        if percent_inc != None:
            inc = percent_inc[sug[word]]
            ax.set_xlabel('date \n \n {} searches increased {}% in {}'.format(sug[word], inc, time_range))
        st.pyplot(fig)


