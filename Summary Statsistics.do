clear
ssc install reghdfe
ssc install ftools

* Import Dataset
import delimited "/nas/longleaf/home/rayrayc/Measuring_Race_and_Sex_Gaps/Final_Clean.csv", stringcols(1 2 5 6 19) clear

replace race = "Hispanic" if race == "Latinx"
replace race = "White" if race == "0_White"
replace counts = 1 if counts <= 100
replace counts = 2 if counts > 100 & counts <= 500
replace counts = 3 if counts > 500 & counts <= 1000
replace counts = 4 if counts > 1000 & counts <= 5000
replace counts = 5 if counts > 5000 & counts <= 10000

*** Reset Index
drop index 
gene index=_n

* Encode str to num to be prepped to be transformed into dummy variables.
* Cannot encode census_tract, more than 65k var.
encode lender_lei, gen(lender_lei_)
encode race, gen(race_)
encode sex, gen(sex_)
encode loan_type, gen(loan_type_)
encode dti_ratio, gen(dti_ratio_)
encode preapproval, gen(preapproval_)
encode state, gen(state_)
encode year, gen(year_)
encode occupancy_type, gen(occupancy_type_)
encode county_code, gen(county_code_)

* Create Summary Statistics 1
tabstat  approved denied  income log_income loan_amount log_loan_amount ltv, statistics(mean sd median) columns(statistics) varwidth(32)

* Create SUmmary Statistics 2
* Note: The output was copied and The Percent of Total was added in Excel.
tab race approved
