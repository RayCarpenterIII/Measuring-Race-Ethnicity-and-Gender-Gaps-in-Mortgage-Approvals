clear
ssc install reghdfe
ssc install ftools

* Import Dataset
import delimited "HMDA_Cleaned.csv", stringcols(1 2 5 6 19) clear

replace race = "Hispanic" if race == "Latinx"
replace counts = 1 if counts <= 100
replace counts = 2 if counts > 100 & counts <= 500
replace counts = 3 if counts > 500 & counts <= 1000
replace counts = 4 if counts > 1000 & counts <= 5000
replace counts = 5 if counts > 5000 & counts <= 10000

* Encode str to num to be prepped to be transformed into dummy variables.
* Cannot encode census_tract, more than 65k var.
encode lender_lei, gen(lender_lei_long)
encode race, gen(race_long)
encode sex, gen(sex_long)
encode loan_type, gen(loan_type_long)
encode dti_ratio, gen(dti_ratio_long)
encode preapproval, gen(preapproval_long)
encode state, gen(state_long)
encode year, gen(year_long)
encode occupancy_type, gen(occupancy_type_long)
encode county_code, gen(county_code_long)

* OLS No Controls
eststo: quietly reg approved i.race_long

* OLS With Controls, counts variable is used here instead of the lender variable due to max variable size.
* Counts is a grouped version of the lender variable.
eststo: quietly reg approved i.race_long i.state_long i.preapproval_long ltv i.dti_ratio_long i.loan_type_long i.counts log_income log_loan_amount i.sex_long i.occupancy_type_long

* Add FE
eststo: quietly reghdfe approved i.race_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.state_long, absorb(i.lender_lei_long)

* Robust SE
eststo: quietly reghdfe approved i.race_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.state_long, absorb(i.lender_lei_long) vce(robust)

* Cluster by State
quietly reghdfe approved i.race_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.state_long, absorb(i.lender_lei_long) cluster(state_long)

* Cluster by Lender
eststo: quietly reghdfe approved i.race_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.state_long, absorb(i.lender_lei_long) cluster(lender_lei_long)

* Lender*County interactions
eststo: quietly reghdfe approved i.race_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.state_long, absorb(i.lender_lei_long i.lender_lei_long#i.county_code_long) cluster(lender_lei_long)

* race*state interactions
eststo: quietly reghdfe approved i.race_long##i.state_long, absorb(i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long i.lender_lei_long) cluster(lender_lei_long)

* Add controls to results
quietly estadd local Controls "-", replace : est1
quietly estadd local Controls "Yes", replace : est2 est3 est4 est5 est6 est7

* Add Fixed Effects to results
quietly estadd local FE "-", replace : est1 est2
quietly estadd local FE "Yes", replace : est3 est4 est5 est6 est7

* Add Standard Errors to results
quietly estadd local SE "-", replace : est1 est2 est3
quietly estadd local SE "Robust", replace : est4
quietly estadd local SE "State", replace : est5 
quietly estadd local SE "Lender", replace : est6 est7

* Add Lender County interactions to results
quietly estadd local LenderCounty "-", replace : est1 est2 est3 est4 est5 est6
quietly estadd local LenderCounty "Yes", replace : est7


* Output1
esttab, cells( b(star fmt(3)) se(par fmt(2))) legend label  title(Measuring Race Gaps in Mortgage Approvals)  keep(3.race_long 2.race_long 4.race_long 5.race_long ) nonumbers mtitles("OLS 1" "OLS 2" "FE 1" "FE 2" "FE 3" "FE 4" "FE 5") s(Controls FE SE LenderCounty r2_a N, label("Controls" "FE" "Standard Errors" "LEI * County" "Adjusted R2" "Observations"))

esttab using "output".csv, cells( b(star fmt(3)) se(par fmt(2))) legend label  title(Measuring Race Gaps in Mortgage Approvals)  keep(3.race_long 2.race_long 4.race_long 5.race_long ) nonumbers mtitles("OLS 1" "OLS 2" "FE 1" "FE 2" "FE 3" "FE 4") s(Controls FE SE LenderCounty r2_a N, label("Controls" "FE" "Standard Errors" "LEI * County" "Adjusted R2" "Observations"))

* Output Extended
esttab using "output_extended".csv, cells( b(star fmt(3)) se(par fmt(2))) legend label  title(Measuring Race Gaps in Mortgage Approvals - Extended) nonumbers mtitles("OLS 1" "OLS 2" "FE 1" "FE 2" "FE 3" "FE 4" "FE 5") s(Controls FE ClusterSE LenderCounty r2_a N, label("Controls" "FE" "Standard Errors" "LEI * County" "Adjusted R2" "Observations"))


