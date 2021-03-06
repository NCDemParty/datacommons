import re, math

from dcapi.aggregates.handlers import execute_top, execute_all
from dcentity.models import Entity, EntityAttribute, BioguideInfo
from piston.handler import BaseHandler
from piston.utils import rc
from urllib import unquote_plus
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID


get_totals_stmt = """
    select cycle,
            coalesce(contributor_count,  0)::integer,
            coalesce(recipient_count,    0)::integer,
            coalesce(contributor_amount, 0)::float,
            coalesce(recipient_amount,   0)::float,
            coalesce(l.count,            0)::integer,
            coalesce(firm_income,        0)::float,
            coalesce(non_firm_spending,  0)::float,
            coalesce(grant_count,        0)::integer,
            coalesce(contract_count,     0)::integer,
            coalesce(loan_count,         0)::integer,
            coalesce(grant_amount,       0)::float,
            coalesce(contract_amount,    0)::float,
            coalesce(loan_amount,        0)::float,
            coalesce(e.count,            0)::integer,
            coalesce(e.amount,           0)::float,
            coalesce(cm.count,           0)::integer,
            coalesce(epa.count,          0)::integer,
            coalesce(r.docket_count,     0)::integer,
            coalesce(r.document_count,   0)::integer,
            coalesce(rs.docket_count,    0)::integer,
            coalesce(rs.document_count,  0)::integer,
            coalesce(f.member_count,     0)::integer,
            coalesce(f.committee_count,  0)::integer,
            coalesce(indexp.spending_amount, 0)::float,
            coalesce(fec_committee.total_raised, 0)::float,
            coalesce(fec_committee.count, 0)::integer
    from
         (select *
         from agg_entities
         where entity_id = %s) c
    full outer join
         (select *
         from agg_lobbying_by_cycle_rolled_up
         where entity_id = %s) l
    using (cycle)
    full outer join
         (select *
         from agg_spending_totals
         where recipient_entity = %s) s
    using (cycle)
    full outer join
         (select *
         from agg_earmark_totals
         where entity_id = %s) e
    using (cycle)
    full outer join (
        select cycle, count
        from agg_pogo_totals
        where entity_id = %s) cm
    using (cycle)
    full outer join (
        select cycle, count
        from agg_epa_echo_totals
        where entity_id = %s) epa
    using (cycle)
    full outer join (
        select cycle, docket_count, document_count
        from agg_regulations_text_totals
        where entity_id = %s) r
    using (cycle)
    full outer join (
        select cycle, docket_count, document_count
        from agg_regulations_submitter_totals
        where entity_id = %s) rs
    using (cycle)
    full outer join (
        select cycle, member_count, committee_count
        from agg_faca_totals
        where org_id = %s) f
    using (cycle)
    full outer join (
        select cycle, spending_amount
        from agg_fec_indexp_totals
        where entity_id = %s) indexp
    using (cycle)
    full outer join (
        select cycle, total_raised, count
        from agg_fec_committee_summaries
        where entity_id = %s) fec_committee
    using (cycle)
"""


def get_totals(entity_id):
    totals = dict()
    for row in execute_top(get_totals_stmt, *[entity_id] * 11):
        totals[row[0]] = dict(zip(EntityHandler.totals_fields, row[1:]))
    return totals


class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)

    totals_fields = ['contributor_count', 'recipient_count', 'contributor_amount', 'recipient_amount',
                     'lobbying_count', 'firm_income', 'non_firm_spending',
                     'grant_count', 'contract_count', 'loan_count', 'grant_amount', 'contract_amount', 'loan_amount',
                     'earmark_count', 'earmark_amount',
                     'contractor_misconduct_count',
                     'epa_actions_count',
                     'regs_docket_count', 'regs_document_count', 'regs_submitted_docket_count', 'regs_submitted_document_count',
                     'faca_member_count', 'faca_committee_count',
                     'independent_expenditure_amount', 'fec_total_raised', 'fec_summary_count']
    ext_id_fields = ['namespace', 'id']

    def read(self, request, entity_id):

        try:
            entity_id = UUID(entity_id)
            entity = Entity.objects.select_related().get(id=entity_id)
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        except ValueError:
            return rc.NOT_FOUND

        totals = get_totals(entity_id)

        external_ids = [{'namespace': attr.namespace, 'id': attr.value} for attr in entity.attributes.all()]

        result = {'name': entity.name,
                  'id': entity.id,
                  'type': entity.type,
                  'totals': totals,
                  'external_ids': external_ids,
                  'metadata': entity.metadata}

        return result


class EntityAttributeHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ['id']

    def read(self, request):
        namespace = request.GET.get('namespace', None)
        bioguide_id = request.GET.get('bioguide_id', None)
        id = request.GET.get('id', None)

        if (not id or not namespace) and not bioguide_id:
            error_response = rc.BAD_REQUEST
            error_response.write("Must include a 'namespace' and an 'id' parameter or a 'bioguide_id' parameter.")
            return error_response

        if bioguide_id:
            entities = BioguideInfo.objects.filter(bioguide_id=bioguide_id)
        else:
            entities = EntityAttribute.objects.filter(namespace=namespace, value=id)

        return [{'id': e.entity_id} for e in entities]


class EntitySearchHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = [
        'id', 'name', 'type',
        'count_given', 'count_received', 'count_lobbied',
        'total_given', 'total_received', 'firm_income', 'non_firm_spending',
        'state', 'party', 'seat', 'lobbying_firm', 'is_superpac'
    ]

    stmt = """
        select
            e.id, e.name, e.type,
            coalesce(a.contributor_count,   0)::integer,
            coalesce(a.recipient_count,     0)::integer,
            coalesce(l.count,               0)::integer,
            coalesce(a.contributor_amount,  0)::float,
            coalesce(a.recipient_amount,    0)::float,
            coalesce(l.firm_income,         0)::float,
            coalesce(l.non_firm_spending,   0)::float,
            pm.state, pm.party, pm.seat, om.lobbying_firm, om.is_superpac
        from matchbox_entity e
        inner join (select distinct entity_id
                    from matchbox_entityalias ea
                    where to_tsvector('datacommons', ea.alias) @@ to_tsquery('datacommons', quote_literal(%s))) ft_match
            on e.id = ft_match.entity_id
        left join politician_metadata_latest_cycle_view pm
            on e.id = pm.entity_id
        left join organization_metadata_latest_cycle_view om
            on e.id = om.entity_id
        left join agg_lobbying_by_cycle_rolled_up l
            on e.id = l.entity_id and l.cycle = -1
        left join agg_entities a
            on e.id = a.entity_id and a.cycle = -1
        where case when e.type = 'politician' then a.recipient_count > 0 or a.recipient_amount > 0 else 't' end
    """

    def read(self, request):
        query = request.GET.get('search')
        entity_type = request.GET.get('type')
        if not query:
            error_response = rc.BAD_REQUEST
            error_response.write("Must include a query in the 'search' parameter.")
            return error_response

        stmt = self.stmt

        if entity_type:
            stmt += '\n        and e.type = %s'

        parsed_query = ' & '.join(re.split(r'[ &|!():*]+', unquote_plus(query)))
        query_params = (parsed_query)
        query_params = [x for x in (parsed_query, entity_type) if x]
        raw_result = execute_top(stmt, *query_params)

        return [dict(zip(self.fields, row)) for row in raw_result]


# GIANT HACK - mangle get_totals_stmt, above, to also do something useful for search
search_totals_stmt = get_totals_stmt
for subselect in re.findall(r"\(\s*select[^\)]*\)[\s_a-z]*using \(cycle\)", search_totals_stmt, flags=re.DOTALL):
    if "org_id" in subselect:
        nsub = subselect.replace("select cycle", "select org_id").replace("using (cycle)", "on entity_id = org_id")
    elif "recipient_entity" in subselect:
        nsub = subselect.replace("select cycle", "select recipient_entity").replace("using (cycle)", "on entity_id = recipient_entity")
    else:
        nsub = subselect.replace("select cycle", "select entity_id").replace("using (cycle)", "using (entity_id)")
    search_totals_stmt = search_totals_stmt.replace(subselect, nsub)
search_totals_stmt = search_totals_stmt.replace("select cycle", "select entity_id").replace("= %s", "in (%s) and cycle = -1")

valid_seats = set(['federal:house', 'federal:president', 'federal:senate', 'state:governor', 'state:judicial', 'state:lower', 'state:office', 'state:upper'])
valid_states = set(['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO',\
    'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY'])
valid_parties = set(['D', 'R', 'O'])

class EntityAdvSearchHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = ['id', 'name', 'type', 'score']

    stmt = """
        select
            e.id, e.name, e.type,
            case e.type
                when 'politician' then
                    2 * coalesce(ae.recipient_amount, 0) / 715550915
                when 'individual' then
                    coalesce(ae.contributor_amount, 0) / 73301345.75 +
                    coalesce(al.count, 0) / 8882
                when 'organization' then
                    coalesce(ae.contributor_amount, 0) / 364255258.20 +
                    coalesce(al.non_firm_spending, 0) / 969305680.0 +
                    coalesce(al.firm_income, 0) / 560548185.0
                when 'industry' then
                    coalesce(ae.contributor_amount, 0) / 3648608028.38 +
                    coalesce(al.non_firm_spending, 0) / 5757475979.0 +
                    coalesce(al.firm_income, 0) / 2225030909.0
                else 0
            end score
        from matchbox_entity e
        inner join (
            select distinct entity_id
                from matchbox_entityalias ea
                where to_tsvector('datacommons', ea.alias) @@ to_tsquery('datacommons', quote_literal(%s))
        ) ft_match on e.id = ft_match.entity_id
        left join agg_entities ae on e.id = ae.entity_id and ae.cycle = -1
        left join agg_lobbying_by_cycle_rolled_up al on e.id = al.entity_id and al.cycle = -1
        JOINS
        WHERE
        order by score desc, e.id asc
    """

    def read(self, request):
        query = request.GET.get('search')
        if not query:
            error_response = rc.BAD_REQUEST
            error_response.write("Must include a query in the 'search' parameter.")
            return error_response

        stmt = self.stmt

        per_page = min(int(request.GET.get('per_page', 10)), 25)
        page = max(int(request.GET.get('page', 1)), 1)
        start = (page - 1) * per_page
        end = start + per_page

        parsed_query = ' & '.join(re.split(r'[ &|!():*]+', unquote_plus(query)))
        where_filters = []
        extra_joins = []
        filters = {}

        subtype_raw = request.GET.get('subtype', None)
        subtype = subtype_raw if subtype_raw in set(('contributors', 'lobbyists', 'politicians', 'industries', 'lobbying_firms', 'political_groups', 'other_orgs')) else None
        if subtype:
            if subtype == 'contributors':
                where_filters.append("e.type = 'individual' and mbim.is_contributor = 't'")
                extra_joins.append("left join matchbox_individualmetadata mbim on e.id = mbim.entity_id")
            elif subtype == 'lobbyists':
                where_filters.append("e.type = 'individual' and mbim.is_lobbyist = 't'")
                extra_joins.append("left join matchbox_individualmetadata mbim on e.id = mbim.entity_id")
            elif subtype == 'politicians':
                where_filters.append("e.type = 'politician'")
                
                # check for seat and state
                seat = request.GET.get('seat', None)
                seat = seat if seat in valid_seats else None

                state = request.GET.get('state', None)
                state = state if state in valid_states else None

                party = request.GET.get('party', None)
                party = party if party in valid_parties else None

                if state or seat or party:
                    pol_filters = ["state = '%s'" % state if state else None, "seat = '%s'" % seat if seat else None]
                    if party:
                        if party in ('R', 'D'):
                            pol_filters.append("party = '%s'" % party)
                        else:
                            pol_filters.append("party not in ('R', 'D')")
                    pol_where = " and ".join(filter(lambda x:x, pol_filters))
                    extra_joins.append("inner join (select distinct on (entity_id) * from matchbox_politicianmetadata where %s order by entity_id, cycle desc) mbpm on e.id = mbpm.entity_id" % pol_where)
            elif subtype == 'industries':
                where_filters.append("e.type = 'industry'")
            elif subtype == 'lobbying_firms':
                where_filters.append("e.type = 'organization' and mbom.lobbying_firm = 't'")
                extra_joins.append("left join (select distinct on (entity_id) * from matchbox_organizationmetadata order by entity_id, cycle desc) mbom on e.id = mbom.entity_id")
            elif subtype == 'political_groups':
                where_filters.append("e.type = 'organization'")
                extra_joins.append("inner join (select distinct on (entity_id) * from matchbox_entityattribute where namespace = 'urn:fec:committee') mbea on e.id = mbea.entity_id")
            elif subtype == 'other_orgs':
                where_filters.append("e.type = 'organization' and mbom.lobbying_firm = 'f'")
                where_filters.append("(coalesce(mbea.value, '') = '' or mbom.is_corporation = 't' or mbom.is_cooperative = 't' or mbom.is_corp_w_o_capital_stock = 't')")
                extra_joins.append("left join (select distinct on (entity_id) * from matchbox_entityattribute where namespace = 'urn:fec:committee') mbea on e.id = mbea.entity_id")
                extra_joins.append("left join (select distinct on (entity_id) * from matchbox_organizationmetadata order by entity_id, cycle desc) mbom on e.id = mbom.entity_id")
        else:
            # subtype implies type, so only use explicit type if there's not a subtype
            etype_raw = request.GET.get('type', None)
            if etype_raw:
                allowed_types = set(('organization', 'industry', 'individual', 'politician'))
                entity_type = [etype for etype in etype_raw.split(',') if etype in allowed_types]
                if entity_type:
                    where_filters.append("e.type in (%s)" % ','.join(["'%s'" % etype for etype in entity_type]))
                    filters['type'] = entity_type

        where_clause = "where %s" % (" and ".join(where_filters)) if where_filters else ""
        join_clause = " ".join(extra_joins)

        query_params = (parsed_query,)
        raw_result = execute_top(stmt.replace("WHERE", where_clause).replace("JOINS", join_clause), *query_params)

        total = len(raw_result)
        results = [dict(zip(self.fields, row)) for row in raw_result[start:end]]

        print raw_result, results

        if total:
            ids = ','.join(["'%s'" % row['id'] for row in results])

            totals = dict()
            for row in execute_top(search_totals_stmt.replace("%s", ids)):
                totals[row[0]] = dict(zip(EntityHandler.totals_fields, row[1:]))

            # grab the metadata
            entities = {e.id: e for e in Entity.objects.select_related().filter(id__in=[row['id'] for row in results])}

            for row in results:
                row['totals'] = totals.get(row['id'], None)

                # match metadata, but strip out year keys
                meta = entities[row['id']].metadata if row['id'] in entities else None
                row['metadata'] = {k: v for k, v in meta.items() if not (type(k) == int or k.isdigit())} if meta else None
                row['external_ids'] = [{'namespace': attr.namespace, 'id': attr.value} for attr in entities[row['id']].attributes.all()] if row['id'] in entities else None

        return {
            'results': results,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': math.ceil(float(total) / per_page),
            'filters': filters
        }


class EntitySimpleHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = ['id', 'name', 'type', 'aliases']

    stmt = """
        select e.id, name, type, case when count(alias) = 0 then ARRAY[]::varchar[] else array_agg(alias) end as aliases
        from matchbox_entity e
        left join matchbox_entityalias a on
            e.id = a.entity_id and e.name != a.alias
        %s -- possible where clause for entity type
        group by e.id, name, type
        order by e.id
        offset %%s
        limit %%s
    """

    count_stmt = """
        select count(*)
        from matchbox_entity
        %s -- possible where clause for entity type
    """

    def read(self, request):
        count = request.GET.get('count')
        start = request.GET.get('start')
        end = request.GET.get('end')
        entity_type = request.GET.get('type')

        if entity_type:
            where_clause = "where type = %s"
        else:
            where_clause = ''

        if count:
            return dict(count=execute_top(self.count_stmt % where_clause, *([entity_type] if entity_type else []))[0][0])

        if start is not None and end is not None:
            try:
                start = int(start)
                end = int(end)
            except:
                error_response = rc.BAD_REQUEST
                error_response.write("Must provide integers for start and end.")
                return error_response
        else:
            error_response = rc.BAD_REQUEST
            error_response.write("Must specify valid start and end parameters.")
            return error_response

        if (end < start or end - start > 10000):
            error_response = rc.BAD_REQUEST
            error_response.write("Only 10,000 entities can be retrieved at a time.")
            return error_response

        raw_result = execute_top(self.stmt % where_clause, *([entity_type] if entity_type else []) + [start, end - start + 1])
        return [dict(zip(self.fields, row)) for row in raw_result]

### METADATA FOR LANDING PAGES
class EntityTypeSummaryHandler(BaseHandler):

    args = ['entity_type', ]
    fields = ['cycle', 'contributions_amount', 'contributions_count', 'entity_count']

    stmt = """
        select
            cycle,
            contributions_amount,
            contributions_count,
            entity_count
        from
            summary_entity_types
        where entity_type = %s;
    """

    def read(self, request, **kwargs):
        totals = dict()
        for row in execute_all(self.stmt, *[kwargs[param] for param in self.args]):
            rowdict = dict(zip(self.fields, row))
            cycle = rowdict.pop('cycle')
            totals[cycle] = rowdict

        result = {'entity_type': kwargs['entity_type'],
                  'totals': totals}
        
        return result
