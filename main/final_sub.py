import pandas as pd
import numpy as np
from datetime import date 



# Calculating ages
def calculateAge(year):
    try:
        today = date.today() 
        age = today.year -  year
    except ValueError:
        pass
    return age 

# Function for cleaning survey data
def clean_survey_df(survey_df):
    
    # Dealing with follow up questions
    survey_df.loc[raw_df['Q8.0 Did you vote in the 2019 General Election?'] == 'No, I do not vote',
                  'Q8.1 If so, how did you vote in the 2019 General Election?'] = "I didn't vote"
    
    # Converting year of birth to age
    years = pd.to_numeric(raw_df['Q21 What is your year of birth?'], errors = 'coerce')
    Respondant_Age = calculateAge(years)
    Respondant_Age = calculateAge(years)
    survey_df['Q21 What is your year of birth?'] = Respondant_Age
    survey_df.rename(columns = {'Q21 What is your year of birth?':'Respondant age'}, inplace = True) 
    
    # Converting post codes to westminster constituencies
    westminster_constituency = pd.merge(survey_df, postcode_lookup, 'left',
                                    left_on=survey_df.columns[9],
                                    right_on= 'postcode').iloc[:,-1]
    survey_df["Q5 What is your postcode? For example, if your postcode is 'SW1A 1AA', please enter 'SW1A 1' - the first part of the postcode and the first digit of the second part."] = westminster_constituency
    survey_df.rename(columns = {"Q5 What is your postcode? For example, if your postcode is 'SW1A 1AA', please enter 'SW1A 1' - the first part of the postcode and the first digit of the second part.":
                         "Respondant constituency"},
              inplace = True) 

    # Removing useless columns
    survey_df.drop(survey_df[survey_df.columns[survey_df.count() < 10]], axis = 1, inplace=True)
    
    # Deleting duplicates
    survey_df.drop_duplicates(subset='respondent_id', inplace=True)
    
    # Normalizing null values
    survey_df.replace(['nan', '-9999', 'np.nan', 'None'],
                      np.nan, inplace=True)
    
    # Resetting the index and returning the cleaned dataframe 
    clean_survey_df = survey_df.reset_index(drop=True)
    
    return clean_survey_df
    


raw_data_fname = r'C:\Users\bless\OneDrive\Documents\focaldatajuniorapplieddatascientist\raw_survey.csv'
postcode_lookup_fname = r'C:\Users\bless\OneDrive\Documents\focaldatajuniorapplieddatascientist\postcode_lookup.csv'

raw_df = pd.read_csv(raw_data_fname)
postcode_lookup = pd.read_csv(postcode_lookup_fname)

clean_df = clean_survey_df(raw_df)



# Adding bad response tags
condition_1 = clean_df['Respondant age'] < 5
condition_2 = clean_df.isnull().sum(axis=1) > 20
condition_3 = ~clean_df.iloc[:,10].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df['Respondant age'] < 22)
condition_4 = ~clean_df.iloc[:,13].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df['Respondant age'] < 21)
condition_5 = ~clean_df.iloc[:,11].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df['Respondant age'] < 19)
condition_6 = ~clean_df.iloc[:,12].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df['Respondant age'] < 19)

condition_7 = (clean_df.end_time.apply(pd.to_datetime) - 
                         clean_df.start_time.apply(pd.to_datetime)) / pd.Timedelta(minutes=1) < 5

clean_df.loc[condition_1|condition_2|condition_3|condition_4
              |condition_5|condition_6|condition_7, 'is_bad_respondant'] = 'yes'
















