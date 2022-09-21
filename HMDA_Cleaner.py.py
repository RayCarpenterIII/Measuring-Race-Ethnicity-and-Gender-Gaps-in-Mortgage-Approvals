#!/usr/bin/env python
# coding: utf-8

# # HMDA Cleaner

# The purpose of this program is to clean HMDA data further data needs.

### Import HMDA Data, Packages, and Check Dataset.

#Imports packages to be used by program
import pandas as pd
import numpy as np

def HMDA_clean_chunker(dataset, Name_of_Output_CSV):
    #load in dataset.
    
    cleaned_df = pd.DataFrame()
    for i, chunk in enumerate(pd.read_csv(dataset, chunksize=1000000, usecols = ['activity_year', 'lei','state_code', 'county_code',
       'census_tract','action_taken', 'preapproval',
       'loan_type', 'loan_purpose',
       'loan_amount','loan_to_value_ratio',
       'occupancy_type','income', 'debt_to_income_ratio',
       'applicant_ethnicity-1','co-applicant_ethnicity-1',
       'applicant_race-1','co-applicant_race-1',
       'applicant_sex', 'co-applicant_sex','applicant_age'])):
    
        df = chunk
        
        dfa = df.dropna(subset=['applicant_race-1'])
    
        '''
        Clean Race data.
        '''
                        
        #Groups racial categories and adds names.
        #The '0_' in the '0_White' indicates that it will be the ommited variable in a regression.
        df1 = df.replace(to_replace = {'applicant_race-1' : {
                                        (5):'0_White',
                                        (2,21,22,23,24,25,26,27):'Asian',
                                        (3):'Black',
                                        (1, 4,41,42,43,44):'Other',
                                        (6,7):'Not Reported'}})
        #Remove 'Not Reported' rows.
        df2 = df1[df1['applicant_race-1'] != 'Not Reported']
        #Clean Ethnicity Data.
        df3 = df2.replace(to_replace = {'applicant_ethnicity-1' : {
                                    (1,11,14,12,13):1,
                                      (2):0,
                                     (3,4,np.nan):'Not Reported',}})
        #Remove 'Not Reported' rows.
        df4 = df3[df3['applicant_ethnicity-1'] != 'Not Reported']

        #Create Race Column.
        df4 = df4.reset_index()
        race = []
        for row in df4.index:
            if df4['applicant_ethnicity-1'][row] == 1:
                race.append('Latinx')
            else:
                race.append(df4['applicant_race-1'][row])
        df4_copy = df4.copy()
        df4_copy['Race'] = race

        '''
        Clean Income 
        '''
        #Remove rows that had no income reported or an income less than 0.
        def income_reported_to_categorical(table, column):
            values = table[column].values
            new_table = table.copy()
            ir_array =  []
            for i in values:
                if i == np.nan:
                    ir_array.append('No Report')
                elif i <= 0:
                    ir_array.append('Zero_or_Negative')
                elif i > 0:
                    ir_array.append('Reported')
                else:
                    ir_array.append('No_Report')
            new_table['Income Reported'] = ir_array
            return new_table
        #This removes all non reported and 0 or negative rows.
        df6 = income_reported_to_categorical(df4_copy,'income')
        
        df6a = df6.copy()
        df6a['Income Reported'] = df6a['Income Reported'].map(str)
        df7 = df6a[df6a["Income Reported"].str.contains("Reported") == True]
        #Creates log Income column.
        df7_2 = df7.copy()
        df7_2['Log Income'] = np.log(df7['income'])

        '''
        Create approval and denial indicator column.
        This also removes withdrawn applications and other instances that aren't under the Approval or Denial categories.
        '''
                        
        def action_taken_to_approval_indicator(table, column):
            values = table[column].values
            ir_array =  []
            for i in values:
                if i == 1:
                    ir_array.append('Approved')
                elif i == 2:
                    ir_array.append('Approved')
                elif i == 3:
                    ir_array.append('Denied')
                else:
                    ir_array.append('other')
            table2 = table.copy()
            table2['Approval Indicator'] = ir_array
            table3 = table2[table2["Approval Indicator"].str.contains("other") == False]
            table4 = pd.get_dummies(table3, columns = ['Approval Indicator'])
            return table4
        df8 = action_taken_to_approval_indicator(df7_2, 'action_taken')

        '''
        Clean applicant sex
        '''
        df9 = df8.replace(to_replace = {'applicant_sex' : {(1):'0_Male',(2):'Female',
                                                          (3,4,6):'Not Applicable'}})
        df10 = df9[df9['applicant_sex'] != 'Not Applicable']
        #df10 = pd.get_dummies(df9, columns = ['applicant_sex'])

        '''
        Clean Loan to Value Ratios
        '''
        #This removes all non-numeric rows.
        df11 = df10[pd.to_numeric(df10['loan_to_value_ratio'], errors = 'coerce').notnull()]

        '''
        Clean Debt to Income    
        '''
        #Creates a second DTI column and changes name for OLS.
        df11_01 = df11.copy()
        df11_01['DTI_Ratio'] = df11_01['debt_to_income_ratio']
        df11_02 = df11_01.replace(to_replace = {'DTI_Ratio': {'<20%':'0%-20%'}})
        #Drops no answer rows.
        df12 = df11_02.dropna(subset=['debt_to_income_ratio'])
        #Drops exempt rows.
        df13 = df12[df12["debt_to_income_ratio"].str.contains("Exempt") == False]
        #Rename Column
        df13_5 = df13.rename(columns = {'debt_to_income_ratio': 'DTI'})
        df13_4 =  pd.get_dummies(df13_5, columns = ['DTI'])


        '''
        Clean Loan Amount and create log(Loan Amount)
        '''
        #This drops all N/A rows.
        df14 = df13_4.dropna(subset=['loan_amount'])
        #This removes all non-numeric rows.
        df15 = df14[pd.to_numeric(df14['loan_amount'], errors = 'coerce').notnull()]
        #This removes all rows with a value less than or equal to 0.
        df16 = df15[~(df15['loan_amount'] <= 0)]
        #Creates log(Loan Amount)
        df16['Log Loan Amount'] = np.log(df16['loan_amount'])

        '''
        Clean Loan Type
        '''
        df17 = df16.replace(to_replace = {'loan_type' : {(1):'Conventional',
                                                        (2): 'FHA',(3): 'VA',
                                                        #USDA Rural Housing Service or Farm Service Agency.
                                                        (4): 'RHS or FSA'}})
        df18 = df17.rename(columns = {'loan_type': 'Loan_Type'})

        '''
        Filter Loan Purpose
        '''
        #This study is only interested in Home Purchase loans.
        #It is leaving out home improvement, refinancing, Cash-out refinanciing, Not applicable, and other purposes.
        df20 = df18[df18["loan_purpose"] == 1]

        '''
        Clean Preapproval
        '''
        df21 = df20.replace(to_replace = {'preapproval' : {(1): 'Preapproval Requested',
                                                           (2): '0 No Preapproval Request'}})

        '''
        Compile final Data Frame
        '''
        #Rename columns
        dfrename = df21.rename(columns = {'Approval Indicator_Approved': 'Approved',
                                            'Approval Indicator_Denied': 'Denied',
                                            'income': 'Income',
                                            'applicant_ethnicity-1': 'Ethnicity',
                                            'applicant_sex': 'Sex',
                                            'loan_to_value_ratio': 'LTV',
                                            'loan_amount': 'Loan_Amount',
                                            'denial_reason-1': 'Denial Reason',
                                            'state_code' : 'State',
                                            'county_code':'County_Code',
                                            'census_tract': 'Census_Tract',
                                            'activity_year': 'Year',
                                            'lei': 'Lender_LEI',
                                            'preapproval' : 'Preapproval',
                                            'Log Income':'Log_Income',
                                            'Log Loan Amount': 'Log_Loan_Amount',
                                            'occupancy_type':'Occupancy_Type'})
        #Pull columns
        Final_df = dfrename[['Year','Lender_LEI','State','County_Code','Census_Tract','Approved','Denied', 
                             'Race','Sex','Income','Log_Income', 
                             'Loan_Amount','Log_Loan_Amount','LTV','Loan_Type','DTI_Ratio','Preapproval','Occupancy_Type']]
        #Add index column.
        Final_df2 = Final_df.copy()
        Final_df2 = Final_df2.reset_index()

        '''
        Save the Dataframe to a csv
        '''
        cleaned_df = Final_df2.to_csv('2019_clean_chunks/2019_chunk{}.csv'.format(i), index=False)
    
    '''
    Outputs
    '''
    #return Final_df.head()
    return print('Data written to CSV sucessfully.')

#Run HMDA_cleaner.
#Enter file location in the HMDA_cleaner(r'file_location') format.|
HMDA_clean_chunker(r"year_2019.csv", r'HMDA_Clean_2019')


# ### The CSV is now ready to be used for further descriptive statistics and the LPM.
