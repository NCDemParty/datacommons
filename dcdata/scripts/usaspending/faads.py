from helpers import splitCode, nullable, recovery_act, datestamp, \
        splitInt, correctionLateIndicator
from dcdata.grants.models import Grant


FIELDS = [('unique_transaction_id', None),
                ('transaction_status', None),
                ('fyq', None),
                ('cfda_program_num', None),
                ('sai_number', None),
                ('account_title', None),
                ('recipient_name', None),
                ('recipient_city_code', None),
                ('recipient_city_name', None),
                ('recipient_county_name', None),
                ('recipient_county_code', None),
                ('recipient_zip', None),
                ('recipient_country_code', splitCode),
                ('recipient_type', splitCode),
                ('action_type', splitCode),
                ('agency_code', splitCode),
                ('federal_award_id', None),
                ('federal_award_mod', None),
                ('fed_funding_amount', splitInt),
                ('non_fed_funding_amount', splitInt),
                ('total_funding_amount', splitInt),
                ('obligation_action_date', nullable),
                ('starting_date', nullable),
                ('ending_date', nullable),
                ('assistance_type', splitCode),
                ('record_type', splitCode),
                ('correction_late_ind', correctionLateIndicator),
                ('fyq_correction', None),
                ('principal_place_code', None),
                ('principal_place_state', None),
                ('principal_place_cc', None),
                ('principal_place_zip', None),
                ('principal_place_cd', None),
                ('cfda_program_title', None),
                ('agency_name', None),
                ('project_description', None),
                ('duns_no', None),
                ('duns_conf_code', None),
                ('progsrc_agen_code', None),
                ('progsrc_acnt_code', None),
                ('progsrc_subacnt_code', None),
                ('receip_addr1', None),
                ('receip_addr2', None),
                ('receip_addr3', None),
                ('face_loan_guran', splitInt),
                ('orig_sub_guran', splitInt),
                ('fiscal_year', splitInt),
                ('principal_place_state_code', splitCode),
                ('recip_cat_type', splitCode),
                ('asst_cat_type', splitCode),
                ('recipient_cd', splitCode),
                ('maj_agency_cat', lambda x: splitCode(x)[:Grant._meta.get_field('maj_agency_cat').max_length]),
                ('rec_flag', recovery_act),
                ('uri', None),
                ('recipient_state_code', splitCode)]

CALCULATED_FIELDS = [
    ('imported_on', None, datestamp)
]

