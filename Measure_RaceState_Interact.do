clear
ssc install reghdfe
ssc install ftools

* Import Dataset
import delimited "/nas/longleaf/home/rayrayc/Measuring_Race_and_Sex_Gaps/Final_Clean.csv", stringcols(1 2 5 6 19) clear

replace race = "Hispanic" if race == "Latinx"
replace counts = 1 if counts <= 100
replace counts = 2 if counts > 100 & counts <= 500
replace counts = 3 if counts > 500 & counts <= 1000
replace counts = 4 if counts > 1000 & counts <= 5000
replace counts = 5 if counts > 5000 & counts <= 10000

* Reset Index
drop index
gene index=_n

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

* race*state interactions
eststo: quietly areg approved i.race_long##i.state_long i.year_long i.sex_long  log_income log_loan_amount i.preapproval_long c.ltv##i.dti_ratio_long i.loan_type_long i.occupancy_type_long , absorb(lender_lei_long) cluster(lender_lei_long) 

* Add controls to results
quietly estadd local Controls "Yes", replace : est1

* Add Fixed Effects to results
quietly estadd local FE "Yes", replace : est1

* Add Standard Errors to results

quietly estadd local SE "Lender", replace : est1

* Add Lender County interactions to results
quietly estadd local LenderCounty "-", replace : est1

* Add state*race interactions to results
quietly estadd local RaceState "Yes", replace : est1

esttab using HMDA_state_interact_race.csv, cells( b(star fmt(3)) se(par fmt(2))) legend label  title(Measuring Race and State Interactions) nonumbers mtitles("FE 6") s(Controls FE ClusterSE RaceState r2_a N, label("Controls" "FE" "Standard Errors" "Race * State" "Adjusted R2" "Observations"))