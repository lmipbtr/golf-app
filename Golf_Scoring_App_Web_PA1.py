import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
#import matplotlib as plt
import streamlit as st
import datetime
from datetime import timedelta
#import tkinter as tk
#from tkinter import filedialog,Tk,Button,ttk,messagebox
import math
import sys

with st.container(border=True):
    st.write("Choose an Score History file by clicking Browse Files or dragging and dropping a file into shaded area")
    uploaded_file1 = st.file_uploader("Score History File")
if uploaded_file1 is not None:
    df_score_history = pd.read_excel(uploaded_file1, sheet_name='Score')
    df_score_history['Date'] = pd.to_datetime(df_score_history['Date'],format='%d/%m/%Y')

    df_artificial_rounds = pd.read_excel(uploaded_file1, sheet_name='Artificial Rounds')
    df_artificial_rounds['Date'] = pd.to_datetime(df_artificial_rounds['Date'],format='%d/%m/%Y')

with st.container(border=True):
    st.write("Choose a Course List file by clicking Browse Files or dragging and dropping a file into shaded area")
    uploaded_file2 = st.file_uploader("Course Details File")
if uploaded_file2 is not None:
    df_course_ratings = pd.read_excel(uploaded_file2, sheet_name='Ratings')
    df_course_par_index = pd.read_excel(uploaded_file2,sheet_name='Par_Index')


min_date=(min(df_score_history['Date']) - datetime.timedelta(days=1))#.strftime('%Y-%m-%d')
total_score = 0
total_points = 0
stableford_points = 0
ga_hcap = df_artificial_rounds.iloc[2,3]
initial_SD1 = df_artificial_rounds.iloc[0,2]
initial_SD2 = df_artificial_rounds.iloc[1,2]
initial_SD3 = df_artificial_rounds.iloc[2,2]

df_score_differential = pd.DataFrame()#(columns = ['Date','SD'])
df_round_summary = pd.DataFrame()#(columns = ['Date','SD'])
row1 = pd.DataFrame([{'Date': min_date, 'SD': initial_SD1}])    
row2 = pd.DataFrame([{'Date': min_date, 'SD': initial_SD2}])
row3 = pd.DataFrame([{'Date': min_date, 'SD': initial_SD3}])    
df_score_differential = pd.concat([df_score_differential, row1], ignore_index=True)
df_score_differential = pd.concat([df_score_differential, row2], ignore_index=True)
df_score_differential = pd.concat([df_score_differential, row3], ignore_index=True)

rounds = df_score_history.shape[0]
cols = df_score_history.shape[1]

for i in range (rounds):
    course = df_score_history.iloc[i,1]
    tees = df_score_history.iloc[i,2]
    pcc = df_score_history.iloc[i,3]
    date = df_score_history.iloc[i,0]
    total_score = 0
    total_points = 0
    comp_type = df_score_history.iloc[i,5]
    par_score = df_score_history.iloc[i,6]
    slope = df_course_ratings.loc[(df_course_ratings['Course'] == course) & (df_course_ratings['Tees'] == tees)]['Slope'].iloc[0]
    scratch = df_course_ratings.loc[(df_course_ratings['Course'] == course) & (df_course_ratings['Tees'] == tees)]['Scratch'].iloc[0]
    course_par  = df_course_ratings.loc[(df_course_ratings['Course'] == course) & (df_course_ratings['Tees'] == tees)]['Par'].iloc[0]
    df_hole_par = df_course_par_index.loc[(df_course_par_index['Par_Index'] == 'Par') & (df_course_par_index['Tees'] == tees)]
    df_rating = df_course_par_index.loc[(df_course_par_index['Par_Index'] == 'Index') & (df_course_par_index['Tees'] == tees)]
    df_hole_par.set_index('Course', inplace = True)
    df_rating.set_index('Course', inplace = True)
    daily_hcap = (round(((ga_hcap * slope / 113) + (scratch - 72)) * 0.93,0))
    
    for j in range (7,cols):
        hole_str='Hole'+str(j-6)
        hole_par = df_hole_par.loc[course,hole_str]
        rating = df_rating.loc[course,hole_str]
        hole = j-6
        
        shots = math.floor(daily_hcap/18)
        if ((daily_hcap %18) - rating) >= 0:
            shots = shots + 1
        else:
            pass
        if df_score_history.iloc[i,j] == 'P':
            score = 10
        else:
            score = df_score_history.iloc[i,j]
        net_score =  int(score) - int(shots)
        if (net_score - hole_par) >= 2:
            stableford_points = 0
        elif (net_score - hole_par) == 1:
            stableford_points = 1
        elif (net_score - hole_par) == 0:
            stableford_points = 2
        elif (net_score - hole_par) == -1:
            stableford_points = 3
        elif (net_score - hole_par) == -2:
            stableford_points = 4
        elif (net_score - hole_par) == -3:
            stableford_points = 5
        elif (net_score - hole_par) == -4:
            stableford_points = 6
        else:
            pass
        total_score = total_score + score
        if comp_type == 'SF':
            total_points = total_points + stableford_points
        elif comp_type == 'Par':
            total_points = 36 + par_score
    score_differential = round(((36 - total_points) + daily_hcap + course_par - (scratch + pcc)) * (113 / slope),1)
    new_row = pd.DataFrame([{'Date': date, 'SD': score_differential}])
    df_score_differential = pd.concat([df_score_differential, new_row], ignore_index=True)
    ga_hcap_old = ga_hcap
    if df_score_differential.shape[0] <= 2:
        ga_hcap = df_score_differential['SD'].sort_values().head(1).mean() - 1.0
        branch = 'A'
    elif df_score_differential.shape[0] == 3:
        ga_hcap = df_score_differential['SD'].sort_values().head(1).mean() - 2.0
        branch = 'B'
    elif df_score_differential.shape[0] == 4:
        ga_hcap = df_score_differential['SD'].sort_values().head(1).mean() - 1.0
        branch = 'C'
    elif df_score_differential.shape[0] == 5:
        ga_hcap = df_score_differential['SD'].sort_values().head(1).mean()
        branch = 'D'
    elif df_score_differential.shape[0] == 6:
        ga_hcap = df_score_differential['SD'].sort_values().head(2).mean() - 1.0
        branch = 'E'
    elif df_score_differential.shape[0] == 7:
        ga_hcap = df_score_differential['SD'].sort_values().head(2).mean()
        branch = 'F'
    elif df_score_differential.shape[0] == 8:
        ga_hcap = df_score_differential['SD'].sort_values().head(2).mean()
        branch = 'G'
    elif df_score_differential.shape[0] == 9:
        ga_hcap = df_score_differential['SD'].sort_values().head(3).mean()
        branch = 'H'
    elif df_score_differential.shape[0] == 10:
        ga_hcap = df_score_differential['SD'].sort_values().head(3).mean()
        branch = 'I'
    elif df_score_differential.shape[0] == 11:
        ga_hcap = df_score_differential['SD'].sort_values().head(3).mean()
        branch = 'J'
    elif df_score_differential.shape[0] == 12:
        ga_hcap = df_score_differential['SD'].sort_values().head(4).mean()
        branch = 'K'
    elif df_score_differential.shape[0] == 13:
        ga_hcap = df_score_differential['SD'].sort_values().head(4).mean()
        branch = 'L'
    elif df_score_differential.shape[0] == 14:
        ga_hcap = df_score_differential['SD'].sort_values().head(4).mean()
        branch = 'M'
    elif df_score_differential.shape[0] == 15:
        ga_hcap = df_score_differential['SD'].sort_values().head(5).mean()
        branch = 'N'
    elif df_score_differential.shape[0] == 16:
        ga_hcap = df_score_differential['SD'].sort_values().head(5).mean()
        branch = 'O'
    elif df_score_differential.shape[0] == 17:
        ga_hcap = df_score_differential['SD'].sort_values().head(6).mean()
        branch = 'P'
    elif df_score_differential.shape[0] == 18:
        ga_hcap = df_score_differential['SD'].sort_values().head(6).mean()
        branch = 'Q'
    elif df_score_differential.shape[0] == 19:
        ga_hcap = df_score_differential['SD'].sort_values().head(7).mean()
        branch = 'R'
    elif df_score_differential.shape[0] >= 20:
        df_score_differential_last20 = df_score_differential.sort_values(by=['Date'],ascending=False).head(20)
        ga_hcap = df_score_differential_last20['SD'].sort_values().head(8).mean()
        branch = 'S'
        
        #Soft and Hard Caps
        last_date = df_round_summary['Date'].max()
        first_date = last_date - timedelta(days = 364)
        last_12_months_df = df_round_summary.loc[(df_round_summary['Date'] >= first_date) & (df_round_summary['Date'] <= last_date)]
        low_ga_hcap = last_12_months_df['New GA Handicap'].min()
        soft_cap = low_ga_hcap + 3
        hard_cap = low_ga_hcap + 5
        diff = ga_hcap - low_ga_hcap
        if(ga_hcap>=soft_cap):
            ga_hcap = low_ga_hcap + 3 + (diff -3)/2
            branch = 'S, soft cap'
        elif(ga_hcap>=hard_cap):
            ga_hcap = hard_cap
            branch = 'S, hard cap'
        else:
            branch = 'S, no cap'
            pass
    else:
        branch = 'T'
        pass
    
    #Exceptional Scores
    exceptional_score = round((ga_hcap_old - score_differential),1)
    ga_hcap = round(ga_hcap,1)
    if exceptional_score >= 7.0 and exceptional_score <= 7.9:
        ga_hcap = ga_hcap - 1.0
    elif exceptional_score >= 10.0:
        ga_hcap = ga_hcap -2.0
    else:
        pass
    total_points = int(total_points)
    new_row2 = pd.DataFrame([{'Date': date.date(), 'Course' : course,'Tees':tees,'Stableford Points':total_points,'Daily Handicap' : int(daily_hcap), 'SD': score_differential, 'New GA Handicap' : ga_hcap}])
    df_round_summary = pd.concat([df_round_summary, new_row2], ignore_index=True)
    #print(branch)    

df_round_summary = df_round_summary.set_index(['Date'])
    
st.dataframe(df_round_summary)
    
average_points = df_round_summary['Stableford Points'].mean()

fig = plt.figure(figsize=(18,12))
plt.plot(df_round_summary['New GA Handicap'])
plt.title("GA Handicap Estimate")
plt.grid(which='both')
plt.xlabel('Date')
plt.ylabel('Hcap')
plt.xticks(rotation=45)
st.pyplot(fig)

st.metric(label='Number of rounds scored:',value=str(df_round_summary.shape[0]))
st.metric(label='Average Stableford Points per round:',value=str(round(average_points,1)))
st.metric(label='Latest GA Handicap:',value=str(ga_hcap))
st.metric(label='Latest Daily Handicap:',value=str(daily_hcap)+' ('+tees+' tees)')

hide_comment ='''results_file=filepath+"Handicap Results.txt"

def show_message(msg1):
    messagebox.showinfo("Information", msg1)

show_message('Number of rounds scored: '+str(df_round_summary.shape[0]))
show_message('Average SF Points per round: '+str(round(average_points,1)))
show_message('Latest GA Handicap: '+str(ga_hcap))
show_message('Latest Daily Handicap: '+str(daily_hcap)+' ('+tees+' tees)')
show_message('Results stored in '+results_file)

with open(results_file, 'w') as f:
    sys.stdout = f # Change the standard output to the file we created.
    print('Average Hole strokes, ignoring pick-ups')
    print(df_hole_averages)
    print('--------------------------------------------------------')
    print(df_round_summary.to_string())
    print('--------------------------------------------------------')
    print('Number of rounds scored: ',df_round_summary.shape[0])
    print('Average SF Points per round: ',round(average_points,1))
    print("Latest GA Handicap: ", ga_hcap)
    print('Latest Daily Handicap: '+str(daily_hcap)+' ('+tees+' tees)')
    print('--------------------------------------------------------')
    sys.stdout = original_stdout # Reset the standard output to its original value'''   

