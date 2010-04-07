
-- Contributor Associations

drop table if exists contributor_associations;

create table contributor_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.contributor_name = a.alias
    where
        a.verified = 't'
    union    
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.contributor_ext_id = a.value
    where
        a.verified = 't'
        -- to do: and we'll need individual namespaces?
        and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'));

create index contributor_associations_entity_id on contributor_associations (entity_id);
create index contributor_associations_transaction_id on contributor_associations (transaction_id);  


-- Recipient Associations

drop table if exists recipient_associations;

create table recipient_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.recipient_name = a.alias
    where
        a.verified = 't'
    union    
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.recipient_ext_id = a.value
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:recipient' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction'));


create index recipient_associations_entity_id on recipient_associations (entity_id);
create index recipient_associations_transaction_id on recipient_associations (transaction_id);             


-- Entity Aggregates

drop table if exists agg_entities;

create table agg_entities as
    select e.id as entity_id, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count, 
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from 
        matchbox_entity e
    left join
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from contributor_associations a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id) as contrib_aggs
        on contrib_aggs.entity_id = e.id
    left join
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from recipient_associations a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id) as recip_aggs
        on recip_aggs.entity_id = e.id;

create index agg_entities_entity_id on agg_entities (entity_id);
    

-- Individuals to Candidate

drop table if exists agg_indivs_to_cand_by_cycle;

create table agg_indivs_to_cand_by_cycle as
    select top.recipient_entity, top.contributor_name, top.contributor_entity, top.cycle, top.count, top.amount
    from (select ra.entity_id as recipient_entity, c.contributor_name, coalesce(ca.entity_id, '') as contributor_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        left join contributor_associations ca using (transaction_id)
        where
            (c.contributor_type is null or c.contributor_type in ('', 'I'))
            and c.recipient_type = 'P'
            and c.transaction_type in ('11', '15', '15e', '15j', '22y')
            --and cycle in ('2007', '2008', '2009', '2010')
        group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, ''), cycle) top
    where
        rank <= 10;

create index agg_indivs_to_cand_by_cycle_recipient_entity on agg_indivs_to_cand_by_cycle (recipient_entity);


-- Committees to Candidate

drop table if exists agg_cmtes_to_cand_by_cycle;

create table agg_cmtes_to_cand_by_cycle as
    select top.recipient_entity, top.contributor_name, top.contributor_entity, top.cycle, top.count, top.amount
    from (select ra.entity_id as recipient_entity, c.contributor_name, coalesce(ca.entity_id, '') as contributor_entity, cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        left join contributor_associations ca using (transaction_id)
        where
            contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z')
            --and cycle in ('2007', '2008', '2009', '2010')
        group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, ''), cycle) top
    where
        rank <= 10;

create index agg_cmtes_to_cand_by_cycle_recipient_entity on agg_cmtes_to_cand_by_cycle (recipient_entity); 


-- Industry Categories to Candidate

drop table if exists agg_cats_to_cand_by_cycle;

create table agg_cats_to_cand_by_cycle as
    select top.recipient_entity, top.contributor_category, top.cycle, top.count, top.amount 
    from
        (select ra.entity_id as recipient_entity, c.contributor_category, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        where
            (contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z'))
        or
            ((c.contributor_type is null or c.contributor_type in ('', 'I'))
            and recipient_type = 'P'
            and transaction_type in ('11', '15', '15e', '15j', '22y'))
        --and cycle in ('2007', '2008', '2009', '2010')
        group by ra.entity_id, c.contributor_category, c.cycle) top
    where
        rank <= 10;
        
create index agg_cats_to_cand_by_cycle_recipient_entity on agg_cats_to_cand_by_cycle (recipient_entity);
       
       
-- Industry Category Orders to Candidate

drop table if exists agg_cat_orders_to_cand_by_cycle;

create table agg_cat_orders_to_cand_by_cycle as
    select top.recipient_entity, top.contributor_category, top.contributor_category_order, top.cycle, top.count, top.amount 
    from
        (select ra.entity_id as recipient_entity, c.contributor_category, c.contributor_category_order, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, c.contributor_category, c.cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        where
            (contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z'))
        or
            ((c.contributor_type is null or c.contributor_type in ('', 'I'))
            and recipient_type = 'P'
            and transaction_type in ('11', '15', '15e', '15j', '22y'))
        --and cycle in ('2007', '2008', '2009', '2010')
        group by ra.entity_id, c.contributor_category, c.contributor_category_order, c.cycle) top
    where
        rank <= 10;

create index agg_cat_orders_to_cand_by_cycle_recipient_entity on agg_cat_orders_to_cand_by_cycle (recipient_entity);
        
        
-- Candidates from Individual

drop table if exists agg_cands_from_indiv_by_cycle;

create table agg_cands_from_indiv_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        where
            (c.contributor_type is null or c.contributor_type in ('', 'I'))
            and c.recipient_type = 'P'
            and c.transaction_type in ('11', '15', '15e', '15j', '22y')
            --and cycle in ('2007', '2008', '2009', '2010')
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= 10;

create index agg_cands_from_indiv_by_cycle_contributor_entity on agg_cands_from_indiv_by_cycle (contributor_entity);
    
    
-- Committees from Individual

drop table if exists agg_cmtes_from_indiv_by_cycle;

create table agg_cmtes_from_indiv_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ca.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        where
            (c.contributor_type is null or c.contributor_type in ('', 'I'))
            and c.recipient_type = 'C'
            -- should there by type restrictions?
            -- and cycle in ('2007', '2008', '2009', '2010')
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= 10;
        
create index agg_cmtes_from_indiv_by_cycle_contributor_entity on agg_cmtes_from_indiv_by_cycle (contributor_entity);
    
    
-- Candidates from Committee

drop table if exists agg_cands_from_cmte_by_cycle;

create table agg_cands_from_cmte_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        where
            contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z')
            --and cycle in ('2007', '2008', '2009', '2010')
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= 10;

create index agg_cands_from_cmte_by_cycle_contributor_entity on agg_cands_from_cmte_by_cycle (contributor_entity);


-- Individuals to Committee

drop table if exists agg_indivs_to_cmte_by_cycle;

create table agg_indivs_to_cmte_by_cycle as
    select top.recipient_entity, top.contributor_name, top.contributor_entity, top.cycle, top.count, top.amount
    from (select ra.entity_id as recipient_entity, c.contributor_name, coalesce(ca.entity_id, '') as contributor_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        left join contributor_associations ca using (transaction_id)
        where
            (c.contributor_type is null or c.contributor_type in ('', 'I'))
            and c.recipient_type = 'C'
            -- any type restrictions?
            --and cycle in ('2007', '2008', '2009', '2010')
        group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, ''), cycle) top
    where
        rank <= 10;

create index agg_indivs_to_cmte_by_cycle_recipient_entity on agg_indivs_to_cmte_by_cycle (recipient_entity);

