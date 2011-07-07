from dcapi.aggregates.handlers import EntityTopListHandler



class TopViolationActionsHandler(EntityTopListHandler):

    fields = 'cycle case_id case_name defendant_name defendant_entity defendants_count other_defendants locations amount year'.split()

    stmt = """
        select
            cycle,
            case_id,
            case_name,
            defendant_name,
            defendant_entity,
            count(distinct defennm) as defendants_count,
            array_to_string(array_agg(distinct d.defennm), ', ')as other_defendants,
            array_to_string(array_agg(distinct f.fcltcit || ', ' || f.fcltstc), ', ') as locations,
            amount,
            year
        from agg_epa_echo_actions a
        inner join epa_echo_defendant d on a.case_id = d.enfocnu
        inner join epa_echo_facility f on a.case_id = f.enfocnu
        where
            defendant_entity = %s
            and cycle = %s
        group by cycle, case_id, case_name, defendant_name, defendant_entity, f.fcltcit, f.fcltstc, amount, year
        order by cycle desc, amount desc
        limit %s
    """.format(', '.join(fields))


