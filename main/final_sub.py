import pandas as pd
import numpy as np
from datetime import date 

#############################################################################################################################

                                                    # CLEANING THE DATA #

# Function to calculate ages from year inputs
def calculateAge(year):
    """
    Takes a year integer as input and returns the age as output
    Assumes person was born the 1st day of the given year
    
    Keyword arguments
    year -- year as int

    Returns
    age -- age in years

    """
    try:
        today = date.today() 
        age = today.year -  year
    except ValueError:
        pass
    return age 

# Function for cleaning survey data
def clean_survey_df(survey_df, postcode_mapper):
    
    """
    Cleans the dataframe in the following steps:
        1. Combines results from followup questions
        2. Converts year of birth to age using the calculateAge function
        3. Converts postcodes to constituencies
        4. Removes columns that don't contain any information
        5. Deletes duplicate respondant ids (expectiation is that the same person/id address
                                             should have the same respondant id)
        6. Gives all null values ('-9999', 'None', 'nan' etc) a value of NaN
    
    The dataframe index is then reset
    
    Keyword arguments
    survey_df -- dataframe containing survey data
    postcode_mapper -- dataframe containing postcode and constituency data for mapping
    
    Returns
    clean_survey_df -- A cleaned survey via the steps above
    
    This function makes various assumptions about the structure of the dataframe.
    
    """
    
    # Columns for easy indexing and copy to retain information
    cols = survey_df.columns
    survey_df_copy = survey_df.copy()
    
    # Dealing with follow up questions    
    survey_df_copy.loc[survey_df_copy[cols[11]] == 'No, I do not vote',
              cols[12]] = "I didn't vote"
    
    # Converting year of birth to age
    years = pd.to_numeric(survey_df_copy[cols[69]], errors = 'coerce')
    Respondant_Age = calculateAge(years)
    survey_df_copy[cols[69]] = Respondant_Age
    survey_df_copy.rename(columns = {cols[69]:'Respondant age'}, inplace = True) 
    
    # Converting post codes to westminster constituencies
    westminster_constituency = pd.merge(survey_df_copy, postcode_mapper, 'left',
                                    left_on=survey_df.columns[9],
                                    right_on= 'postcode').iloc[:,-1]
    survey_df_copy[cols[9]] = westminster_constituency
    survey_df_copy.rename(columns = {cols[9]:"Respondant constituency"}, inplace = True) 

    # Removing useless columns
    survey_df_copy.drop(survey_df_copy[survey_df_copy.columns[survey_df_copy.count() < 10]], axis = 1, inplace=True)
    
    # Deleting duplicates
    survey_df_copy.drop_duplicates(subset='respondent_id', inplace=True)
    
    # Normalizing null values
    survey_df.replace(['nan', '-9999', 'np.nan', 'None'],
                      np.nan, inplace=True)
    
    # Resetting the index and returning the cleaned dataframe 
    clean_survey_df = survey_df_copy.reset_index(drop=True)
    
    return clean_survey_df
    

# Loading data and postcode mapping
raw_data_fname = r'C:\Users\bless\OneDrive\Documents\focaldatajuniorapplieddatascientist\raw_survey.csv'
postcode_lookup_fname = r'C:\Users\bless\OneDrive\Documents\focaldatajuniorapplieddatascientist\postcode_lookup.csv'

raw_df = pd.read_csv(raw_data_fname)
postcode_lookup = pd.read_csv(postcode_lookup_fname)

# Clean data and convert relevant columns
clean_df = clean_survey_df(raw_df, postcode_lookup)


################################################################################################################################

                                                # ADDING TAGS TO CLEANED DATA #
# Columns for easy indexing
clean_cols = clean_df.columns

# Condition for respondants with silly ages (oldest is 80, youngest is 1, so about 5 is fine)
condition_1 = clean_df[clean_cols[68]] < 5

# Condition for respondants who don't answer large numebrs of questions
condition_2 = clean_df.isnull().sum(axis=1) > 10

# Condition for respondants who claim to have voted in the 2016 referendum despite being too young
condition_3 = ~clean_df[clean_cols[10]].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df[clean_cols[68]] < 22)

# Condition for respondants who claimed to have voted in the 2017 general election despite being too young
condition_4 = ~clean_df[clean_cols[11]].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df[clean_cols[68]] < 19)

condition_5 = ~clean_df[clean_cols[12]].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df[clean_cols[68]] < 19)

# Condition for respondants who claimed to have voted for a party in the 2017 general election despite being too young
condition_6 = ~clean_df[clean_cols[13]].str.contains(r'\bvote\b',
                                                 na=False) & (clean_df[clean_cols[68]] < 21)

# Condition for respondants who both did and didn't vote 
condition_7 = (clean_df[clean_cols[11]]=="Yes, I voted") & (clean_df[clean_cols[12]] == "No, I didn't vote") 

# Condition for respondants who completed the survey in less than 5 minutes (about 2*std away from the mean time taken)
condition_8 = (clean_df.end_time.apply(pd.to_datetime) - 
                         clean_df.start_time.apply(pd.to_datetime)) / pd.Timedelta(minutes=1) < 5


# Function for tagging respondants upon condition
def tag_upon_conditions(df, conditions_list, new_column, tag):
    """
    Adds a tag upon the rows that fufill a set of conditions in a datafram.
    Assumed the data frame is compatible with the conditions listed.
    
    Keyword arguments
        df -- dataframe to be tagged 
        conditions_list -- qualifiers for tagging 
        new_column -- name of column to store tags
        tag -- name of tag
            
    Returns:
        df_tag -- df with tagged column
    
    """
    # Copy to retain information
    df_tag = df.copy()
    
    # Combine the conditions with bitewise or (any one of the conditions must be met in order to be tagged)
    df_tag.loc[np.bitwise_or.reduce(conditions_list), new_column] = tag
    return df_tag

# List of conditions
cond_list = [condition_1, condition_2, condition_3, condition_4,
             condition_5, condition_6, condition_7, condition_8]

# Tag dataframe
tagged_df = tag_upon_conditions(clean_df,cond_list, 'is_bad_respondant', 'yes' )




