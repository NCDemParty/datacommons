alter table contracts_contract rename government_property to gfe_gfp;
alter table contracts_contract add column verysmallbusinessflag boolean;
alter table contracts_contract add column progsourceagency varchar(2);
alter table contracts_contract add column placeofperformancezipcode varchar(10);
alter table contracts_contract rename contract_financing to contractfinancing;
alter table contracts_contract add column idvpiid varchar(50);
alter table contracts_contract rename naics_code to principalnaicscode;
alter table contracts_contract rename solicitation_id to solicitationid;
alter table contracts_contract add column smallbusinesscompetitivenessdemonstrationprogram boolean;
alter table contracts_contract add column contractingofficerbusinesssizedetermination varchar(1);
alter table contracts_contract rename contract_description to descriptionofcontractrequirement;
alter table contracts_contract add column educationalinstitutionflag boolean;
alter table contracts_contract rename vendor_zipcode to zipcode;
alter table contracts_contract add column clingercohenact boolean;
alter table contracts_contract add column davisbaconact boolean;
alter table contracts_contract rename contract_competitiveness to extentcompeted;
alter table contracts_contract rename cost_data_obtained to costorpricingdata;
alter table contracts_contract rename fed_biz_opps to fedbizopps;
alter table contracts_contract rename last_modified_date to lastmodifieddate;
alter table contracts_contract rename vendor_country_code to vendorcountrycode;
alter table contracts_contract rename vendor_ccr_exception to ccrexception;
alter table contracts_contract add column idvagencyid varchar(4);
alter table contracts_contract rename contract_nia_code to nationalinterestactioncode;
alter table contracts_contract add column firm8aflag boolean;
alter table contracts_contract rename number_of_actions to numberofactions;
alter table contracts_contract add column purchasereason varchar(1);
alter table contracts_contract rename supports_goodness to contingencyhumanitarianpeacekeepingoperation;
alter table contracts_contract add column evaluatedpreference varchar(6);
alter table contracts_contract add column psc_cat varchar(2);
alter table contracts_contract add column walshhealyact boolean;
alter table contracts_contract rename idv_agency_fee to feepaidforuseofservice;
alter table contracts_contract add column veteranownedflag boolean;
alter table contracts_contract rename product_origin_country to countryoforigin;
alter table contracts_contract rename cancellation_date to cancellationdate;
alter table contracts_contract add column a76action boolean;
alter table contracts_contract add column progsourceaccount varchar(4);
alter table contracts_contract rename producer_type to manufacturingorganizationtype;
alter table contracts_contract rename performance_based_contract to performancebasedservicecontract;
alter table contracts_contract add column rec_flag varchar(1) DEFAULT '';
alter table contracts_contract rename vendor_business_name to vendordoingasbusinessname;
alter table contracts_contract add column apaobflag boolean;
alter table contracts_contract add column baobflag boolean;
alter table contracts_contract rename major_program_code to majorprogramcode;
alter table contracts_contract add column transaction_status varchar(32);
alter table contracts_contract add column commercialitemtestprogram boolean;
alter table contracts_contract add column aiobflag varchar(1);
alter table contracts_contract rename contract_action_type to contractactiontype;
alter table contracts_contract add column progsourcesubacct varchar(3);
alter table contracts_contract rename modification_number to modnumber;
alter table contracts_contract add column research varchar(3);
alter table contracts_contract add column type_of_contract BLIMEY!!!;
alter table contracts_contract add column eeparentduns varchar(13);
alter table contracts_contract add column organizationaltype varchar(30);
alter table contracts_contract add column statutoryexceptiontofairopportunity varchar(4);
alter table contracts_contract rename recovered_material_clause to recoveredmaterialclauses;
alter table contracts_contract add column claimantprogramcode varchar(3);
alter table contracts_contract add column interagencycontractingauthority varchar(1);
alter table contracts_contract rename vendor_street_address3 to streetaddress3;
alter table contracts_contract rename vendor_street_address2 to streetaddress2;
alter table contracts_contract rename contract_offers_received to numberofoffersreceived;
alter table contracts_contract add column naobflag boolean;
alter table contracts_contract rename vendor_state to state;
alter table contracts_contract add column servicecontractact boolean;
alter table contracts_contract rename purchase_card_as_payment to purchasecardaspaymentmethod;
alter table contracts_contract rename place_location_code to locationcode;
alter table contracts_contract rename maximum_date to ultimatecompletiondate;
alter table contracts_contract rename transaction_number to transactionnumber;
alter table contracts_contract add column haobflag boolean;
alter table contracts_contract rename place_state_code to statecode;
alter table contracts_contract add column solicitationprocedures varchar(5);
alter table contracts_contract add column womenownedflag boolean;
alter table contracts_contract rename vender_phone to phoneno;
alter table contracts_contract add column srdvobflag boolean;
alter table contracts_contract rename statutory_authority to otherstatutoryauthority;
alter table contracts_contract rename consolidated_contract to consolidatedcontract;
alter table contracts_contract rename requesting_office_id to fundingrequestingofficeid;
alter table contracts_contract rename contract_set_aside to typeofsetaside;
alter table contracts_contract add column placeofperformancecountrycode varchar(3);
alter table contracts_contract rename dod_system_code to systemequipmentcode;
alter table contracts_contract add column tribalgovernmentflag boolean;
alter table contracts_contract rename subcontract_plan to subcontractplan;
alter table contracts_contract rename vendor_city to city;
alter table contracts_contract rename contracting_office_id to contractingofficeid;
alter table contracts_contract add column useofepadesignatedproducts varchar(1);
alter table contracts_contract add column maj_agency_cat varchar(2);
alter table contracts_contract add column hbcuflag boolean;
alter table contracts_contract rename obligated_amount to obligatedamount;
alter table contracts_contract add column stategovernmentflag boolean;
alter table contracts_contract add column pop_cd varchar(4);
alter table contracts_contract add column commercialitemacquisitionprocedures varchar(1);
alter table contracts_contract rename current_amount to baseandexercisedoptionsvalue;
alter table contracts_contract rename contract_pricing_type to typeofcontractpricing;
alter table contracts_contract rename vendor_fax to faxno;
alter table contracts_contract rename id to record_id;
alter table contracts_contract add column nonprofitorganizationflag boolean;
alter table contracts_contract rename it_commercial_availability to informationtechnologycommercialitemcategory;
alter table contracts_contract rename multiyear_contract to multiyearcontract;
alter table contracts_contract add column hubzoneflag boolean;
alter table contracts_contract add column minorityownedbusinessflag boolean;
alter table contracts_contract rename vendor_parent_duns to parentdunsnumber;
alter table contracts_contract add column lettercontract varchar(1);
alter table contracts_contract rename contracting_agency_id to contractingofficeagencyid;
alter table contracts_contract rename product_service_code to productorservicecode;
alter table contracts_contract add column mod_parent varchar(100);
alter table contracts_contract rename cotr_name to cotrname;
alter table contracts_contract add column unique_transaction_id varchar(32);
alter table contracts_contract rename signed_date to signeddate;
alter table contracts_contract add column localgovernmentflag boolean;
alter table contracts_contract rename renewal_date to renewaldate;
alter table contracts_contract add column sdbflag boolean;
alter table contracts_contract add column federalgovernmentflag boolean;
alter table contracts_contract add column seatransportation boolean;
alter table contracts_contract rename completion_date to currentcompletiondate;
alter table contracts_contract rename cotr_other_name to alternatecotrname;
alter table contracts_contract add column fundedbyforeignentity varchar(1);
alter table contracts_contract rename vendor_duns to dunsnumber;
alter table contracts_contract rename contract_bundling_type to contractbundling;
alter table contracts_contract rename vendor_street_address to streetaddress;
alter table contracts_contract rename requesting_agency_id to fundingrequestingagencyid;
alter table contracts_contract rename place_district to congressionaldistrict;
alter table contracts_contract rename vendor_name to vendorname;
alter table contracts_contract add column idvmodificationnumber varchar(25);
alter table contracts_contract add column competitiveprocedures varchar(3);
alter table contracts_contract rename vendor_employees to numberofemployees;
alter table contracts_contract rename maximum_amount to baseandalloptionsvalue;
alter table contracts_contract rename product_origin to placeofmanufacture;
alter table contracts_contract add column placeofperformancecongressionaldistrict varchar(6);
alter table contracts_contract rename modification_reason to reasonformodification;
alter table contracts_contract rename vendor_district to vendor_cd;
alter table contracts_contract rename contract_nocompete_reason to reasonnotcompeted;
alter table contracts_contract add column shelteredworkshopflag boolean;
alter table contracts_contract rename vendor_annual_revenue to annualrevenue;
alter table contracts_contract add column hospitalflag boolean;
alter table contracts_contract rename effective_date to effectivedate;
alter table contracts_contract rename price_difference to priceevaluationpercentdifference;
alter table contracts_contract rename cas_clause to costaccountingstandardsclause;
alter table contracts_contract add column saaobflag boolean;