
-- CONTRIBUTIONS FROM BIGGEST ORGS BY PARTY


select date_trunc('second', now()) || ' -- drop table if exists summary_party_from_biggest_org';
drop table if exists summary_party_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_party_from_biggest_org';
create table summary_party_from_biggest_org as

        select
            organization_entity, name, recipient_party, cycle,
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank
        from
        (select
            organization_entity,
            me.name,
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            cycle,
            count,
            amount
        from
                matchbox_entity me
            inner join
                agg_party_from_org apfo on me.id = apfo.organization_entity
        where
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
            ) three_party
        group by organization_entity, name, recipient_party, cycle;

select date_trunc('second', now()) || ' -- Vcreate index summary_party_from_biggest_org_cycle_rank_idx on summary_party_from_biggest_org (cycle, rank)';
create index summary_party_from_biggest_org_cycle_rank_idx on summary_party_from_biggest_org (cycle, rank);


-- CONTRIBUTIONS FROM BIGGEST ORGS BY FEDERAL/STATE

select date_trunc('second', now()) || ' -- drop table if exists summary_namespace_from_biggest_org';
drop table if exists summary_namespace_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_namespace_from_biggest_org';
create table summary_namespace_from_biggest_org as
        select
            organization_entity,
            me.name,
            transaction_namespace,
            cycle,
            count,
            amount,
            rank() over(partition by transaction_namespace,cycle order by amount desc) as rank
        from
                matchbox_entity me
            inner join
                agg_namespace_from_org apfo on me.id = apfo.organization_entity
        where
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);

select date_trunc('second', now()) || ' -- create index summary_namespace_from_biggest_org_cycle_rank_idx on summary_namespace_from_biggest_org_org (cycle, rank)';
create index summary_namespace_from_biggest_org_cycle_rank_idx on summary_namespace_from_biggest_org (cycle, rank);


-- CONTRIBUTIONS FROM BIGGEST ORGS BY SEAT

select date_trunc('second', now()) || ' -- drop table if exists summary_office_type_from_biggest_org';
drop table if exists summary_office_type_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_office_type_from_biggest_org';
create table summary_office_type_from_biggest_org as
        select
            organization_entity,
            me.name,
            seat,
            cycle,
            count,
            amount,
            rank() over(partition by seat,cycle order by amount desc) as rank
        from
                matchbox_entity me
            inner join
                agg_office_type_from_org apfo on me.id = apfo.organization_entity
        where
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);

select date_trunc('second', now()) || ' -- create index summary_office_type_from_biggest_org_cycle_rank_idx on summary_office_type_from_biggest_org_org (cycle, rank)';
create index summary_office_type_from_biggest_org_cycle_rank_idx on summary_office_type_from_biggest_org (cycle, rank);



-- CONTRIBUTIONS FROM INDIVIDUALS BY PARTY

select date_trunc('second', now()) || ' -- drop table if exists summary_party_from_indiv';
drop table if exists summary_party_from_indiv;

select date_trunc('second', now()) || ' -- create table summary_party_from_indiv';
create table summary_party_from_indiv as

        select
            contributor_entity, name, recipient_party, cycle,
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank
        from
        (select
            contributor_entity,
            me.name,
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            cycle,
            count,
            amount
        from
                matchbox_entity me
            inner join
                agg_party_from_indiv apfi on me.id = apfi.contributor_entity
            ) three_party
        group by contributor_entity, name, recipient_party, cycle
        ;

select date_trunc('second', now()) || ' -- Vcreate index summary_party_from_indiv_idx on summary_party_from_indiv (contributor_entity, cycle)';
create index summary_party_from_indiv_idx on summary_party_from_indiv (contributor_entity, recipient_party, cycle);

-- CONTRIBUTIONS FROM INDIVIDUALS BY FEDERAL/STATE

 select date_trunc('second', now()) || ' -- drop table if exists summary_namespace_from_indiv';
 drop table if exists summary_namespace_from_indiv;

 select date_trunc('second', now()) || ' -- create table summary_namespace_from_indiv';
 create table summary_namespace_from_indiv as
         select
             contributor_entity,
             me.name,
             transaction_namespace,
             cycle,
             count,
             amount,
             rank() over(partition by transaction_namespace,cycle order by amount desc) as rank
         from
                 matchbox_entity me
             inner join
                 agg_namespace_from_indiv anfo on me.id = anfo.contributor_entity
   ;

 select date_trunc('second', now()) || ' -- create index summary_namespace_from_indiv_idx on summary_namespace_from_indiv_org (contributor_entity, cycle)';
 create index summary_namespace_from_indiv_idx on summary_namespace_from_indiv (contributor_entity, transaction_namespace, cycle);

 -- CONTRIBUTIONS FROM INDIVIDUALS BY SEAT

 select date_trunc('second', now()) || ' -- drop table if exists summary_office_type_from_indiv';
 drop table if exists summary_office_type_from_indiv;

 select date_trunc('second', now()) || ' -- create table summary_office_type_from_indiv';
 create table summary_office_type_from_indiv as
         select
             contributor_entity,
             me.name,
             seat,
             cycle,
             count,
             amount,
             rank() over(partition by seat,cycle order by amount desc) as rank
         from
                 matchbox_entity me
             inner join
                 agg_office_type_from_indiv aofi on me.id = aofi.contributor_entity
   ;

 select date_trunc('second', now()) || ' -- create index summary_office_type_from_indiv_idx on summary_office_type_from_indiv (contributor_entity, cycle)';
 create index summary_office_type_from_indiv_idx on summary_office_type_from_indiv (contributor_entity, seat, cycle);

 -- CONTRIBUTIONS FROM INDIVIDUALS BY GROUP/POLITICIAN

 select date_trunc('second', now()) || ' -- drop table if exists summary_recipient_type_from_indiv';
 drop table if exists summary_recipient_type_from_indiv;

 select date_trunc('second', now()) || ' -- create table summary_recipient_type_from_indiv';
 create table summary_recipient_type_from_indiv as
       with individual_contributions_by_cycle as (
         select ca.entity_id as contributor_entity, me.name, recipient_type, cycle, count(*), sum(c.amount) as amount
         from (table contributions_individual union all table contributions_individual_to_organization) c
         inner join contributor_associations ca using (transaction_id)
         inner join matchbox_entity me on me.id = ca.entity_id
         where c.contributor_ext_id != ''
         group by ca.entity_id, me.name, recipient_type, cycle
      )

      (select
         contributor_entity,
         name,
         recipient_type,
         cycle,
         count,
         amount,
         rank() over (partition by recipient_type, cycle order by sum(amount) desc) as rank
      from
         individual_contributions_by_cycle
     group by contributor_entity, name, recipient_type, cycle, count, amount

     )

      union all

      select contributor_entity, name, recipient_type, -1, count, amount, rank() over (partition by recipient_type order by sum(amount) desc) as rank
      from (
          select contributor_entity, name, recipient_type, sum(count) as count, sum(amount) as amount
          from individual_contributions_by_cycle
          group by contributor_entity, name, recipient_type
      ) x
     group by contributor_entity, name, recipient_type, count, amount;

  select date_trunc('second', now()) || ' -- create index agg_cands_from_indiv_idx on agg_cands_from_indiv (contributor_entity, cycle)';
  create index summary_recipient_type_from_indiv_idx on summary_recipient_type_from_indiv (contributor_entity, cycle);


-- CONTRIBUTIONS FROM CONTRIBUTORS BY PARTY

select date_trunc('second', now()) || ' -- drop table if exists summary_party_from_contrib';
drop table if exists summary_party_from_contrib;

select date_trunc('second', now()) || ' -- create table summary_party_from_contrib';
create table summary_party_from_contrib as

        select
            contributor_entity,
            name,
            recipient_party,
            cycle,
            count,
            amount,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank
        from
            summary_party_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 'f'
        group by contributor_entity, name, recipient_party, cycle, count, amount
        ;

select date_trunc('second', now()) || ' -- Vcreate index summary_party_from_contrib_idx on summary_party_from_contrib (contributor_entity, cycle)';
create index summary_party_from_contrib_idx on summary_party_from_contrib (contributor_entity, recipient_party, cycle);

-- CONTRIBUTIONS FROM CONTRIBUTORS BY FEDERAL/STATE

 select date_trunc('second', now()) || ' -- drop table if exists summary_namespace_from_contrib';
 drop table if exists summary_namespace_from_contrib;

 select date_trunc('second', now()) || ' -- create table summary_namespace_from_contrib';
 create table summary_namespace_from_contrib as
         select
             contributor_entity,
             name,
             transaction_namespace,
             cycle,
             count,
             amount,
             rank() over(partition by transaction_namespace,cycle order by amount desc) as rank
         from
            summary_namespace_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 'f'
            group by contributor_entity, name, transaction_namespace, cycle, count, amount
   ;

 select date_trunc('second', now()) || ' -- create index summary_namespace_from_contrib_idx on summary_namespace_from_contrib_org (contributor_entity, cycle)';
 create index summary_namespace_from_contrib_idx on summary_namespace_from_contrib (contributor_entity, transaction_namespace, cycle);

 -- CONTRIBUTIONS FROM CONTRIBUTORS BY SEAT

 select date_trunc('second', now()) || ' -- drop table if exists summary_office_type_from_contrib';
 drop table if exists summary_office_type_from_contrib;
 create table summary_office_type_from_contrib as
         select
             contributor_entity,
             name,
             seat,
             cycle,
             count,
             amount,
             rank() over(partition by seat,cycle order by amount desc) as rank
         from
            summary_office_type_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 'f'
            group by contributor_entity, name, seat, cycle, count, amount
   ;

 select date_trunc('second', now()) || ' -- create index summary_office_type_from_contrib_idx on summary_office_type_from_contrib (contributor_entity, cycle)';
 create index summary_office_type_from_contrib_idx on summary_office_type_from_contrib (contributor_entity, seat, cycle);

 -- CONTRIBUTIONS FROM CONTRIBUTORS BY GROUP/POLITICIAN

 select date_trunc('second', now()) || ' -- drop table if exists summary_recipient_type_from_contrib';
 drop table if exists summary_recipient_type_from_contrib;

 select date_trunc('second', now()) || ' -- create table summary_recipient_type_from_contrib';
 create table summary_recipient_type_from_contrib as

      select
         contributor_entity,
         name,
         recipient_type,
         cycle,
         count,
         amount,
         rank() over (partition by recipient_type, cycle order by sum(amount) desc) as rank
      from
        summary_recipient_type_from_indiv s
        inner join
        matchbox_individualmetadata im on s.contributor_entity = im.entity_id
        where im.is_contributor = 't' and im.is_lobbyist = 'f'
        group by contributor_entity,name, recipient_type, cycle, count, amount
;

  select date_trunc('second', now()) || ' -- create index agg_cands_from_contrib_idx on agg_cands_from_contrib (contributor_entity, cycle)';
  create index summary_recipient_type_from_contrib_idx on summary_recipient_type_from_contrib (contributor_entity, cycle);


-- CONTRIBUTIONS FROM LOBBYISTS BY PARTY

select date_trunc('second', now()) || ' -- drop table if exists summary_party_from_lobbyist';
drop table if exists summary_party_from_lobbyist;

select date_trunc('second', now()) || ' -- create table summary_party_from_lobbyist';
create table summary_party_from_lobbyist as

        select
            contributor_entity,
            name,
            recipient_party,
            cycle,
            count,
            amount,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank
        from
            summary_party_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 't'
        group by contributor_entity, name, recipient_party, cycle, count, amount
        ;

select date_trunc('second', now()) || ' -- create index summary_party_from_lobbyist_idx on summary_party_from_lobbyist (contributor_entity, cycle)';
create index summary_party_from_lobbyist_idx on summary_party_from_lobbyist (contributor_entity, recipient_party, cycle);

-- CONTRIBUTIONS FROM LOBBYISTS BY FEDERAL/STATE

 select date_trunc('second', now()) || ' -- drop table if exists summary_namespace_from_lobbyist';
 drop table if exists summary_namespace_from_lobbyist;

 select date_trunc('second', now()) || ' -- create table summary_namespace_from_lobbyist';
 create table summary_namespace_from_lobbyist as
         select
             contributor_entity,
             name,
             transaction_namespace,
             cycle,
             count,
             amount,
             rank() over(partition by transaction_namespace,cycle order by amount desc) as rank
         from
            summary_namespace_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 't'
            group by contributor_entity, name, transaction_namespace, cycle, count, amount
   ;

 select date_trunc('second', now()) || ' -- create index summary_namespace_from_lobbyist_idx on summary_namespace_from_lobbyist_org (contributor_entity, cycle)';
 create index summary_namespace_from_lobbyist_idx on summary_namespace_from_lobbyist (contributor_entity, transaction_namespace, cycle);

 -- CONTRIBUTIONS FROM LOBBYISTS BY SEAT

 select date_trunc('second', now()) || ' -- drop table if exists summary_office_type_from_lobbyist';
 drop table if exists summary_office_type_from_lobbyist;
 create table summary_office_type_from_lobbyist as
         select
             contributor_entity,
             name,
             seat,
             cycle,
             count,
             amount,
             rank() over(partition by seat,cycle order by amount desc) as rank
         from
            summary_office_type_from_indiv s
            inner join
            matchbox_individualmetadata im on s.contributor_entity = im.entity_id
            where im.is_contributor = 't' and im.is_lobbyist = 't'
            group by contributor_entity, name, seat, cycle, count, amount
   ;

 select date_trunc('second', now()) || ' -- create index summary_office_type_from_lobbyist_idx on summary_office_type_from_lobbyist (contributor_entity, cycle)';
 create index summary_office_type_from_lobbyist_idx on summary_office_type_from_lobbyist (contributor_entity, seat, cycle);

 -- CONTRIBUTIONS FROM LOBBYISTS BY GROUP/POLITICIAN

 select date_trunc('second', now()) || ' -- drop table if exists summary_recipient_type_from_lobbyist';
 drop table if exists summary_recipient_type_from_lobbyist;

 select date_trunc('second', now()) || ' -- create table summary_recipient_type_from_lobbyist';
 create table summary_recipient_type_from_lobbyist as

      select
         contributor_entity,
         name,
         recipient_type,
         cycle,
         count,
         amount,
         rank() over (partition by recipient_type, cycle order by sum(amount) desc) as rank
      from
        summary_recipient_type_from_indiv s
        inner join
        matchbox_individualmetadata im on s.contributor_entity = im.entity_id
        where im.is_contributor = 't' and im.is_lobbyist = 't'
        group by contributor_entity,name, recipient_type, cycle, count, amount
;

  select date_trunc('second', now()) || ' -- create index agg_cands_from_lobbyist_idx on agg_cands_from_lobbyist (contributor_entity, cycle)';
  create index summary_recipient_type_from_lobbyist_idx on summary_recipient_type_from_lobbyist (contributor_entity, cycle);
