from time import time
import sys

from urllib import unquote_plus
from django.db.models import Q
from piston.handler import BaseHandler
from dcentity.models import Entity, Normalization
from dcdata.contribution.models import Contribution
from dcapi.contributions import filter_contributions
from dcentity.queries import search_entities_by_name
# aggregates imports
from dcapi.aggregates.queries import get_top_contributors, get_top_recipients

RESERVED_PARAMS = ('apikey','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 100000

CONTRIBUTION_FIELDS = ['cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'filing_id', 'is_amendment',
              'amount', 'date', 'contributor_name', 'contributor_ext_id', 'contributor_type', 'contributor_occupation', 
              'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order', 'organization_name', 
              'organization_ext_id', 'parent_organization_name', 'parent_organization_ext_id', 'recipient_name',
              'recipient_ext_id', 'recipient_party', 'recipient_type', 'recipient_category', 'recipient_category_order',
              'committee_name', 'committee_ext_id', 'committee_party', 'election_type', 'district', 'seat', 'seat_status',
              'seat_result']

def load_contributions(params, nolimit=False, ordering=True):
    
    start_time = time()

    per_page = min(int(params.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
    page = int(params.get('page', 1)) - 1
    
    offset = page * per_page
    limit = offset + per_page
    
    for param in RESERVED_PARAMS:
        if param in params:
            del params[param]
            
    unquoted_params = dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    result = filter_contributions(unquoted_params)
    if ordering:
        #result = result.order_by('-contributor_city','contributor_state')
        result = result.order_by('-cycle','-amount')
    if not nolimit:
        result = result[offset:limit]
        
    #print("load_contributions(%s) returned %s results in %s seconds." % (unquoted_params, len(result), time() - start_time))
          
    return result


class ContributionFilterHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = CONTRIBUTION_FIELDS
    model = Contribution
    
    def read(self, request):
        params = request.GET.copy()
        return load_contributions(params)

        


