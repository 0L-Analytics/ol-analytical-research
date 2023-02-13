with base as (select account_type, sum(balance / 1000000) as balance, sum(unlocked) as unlocked from accountbalance where balance > 0 group by account_type), bla as ( select account_type, balance, unlocked, case account_type when 'basic' then balance when 'validator' then unlocked when 'miner' then balance else 0 end as liquid from base) select account_type, balance, unlocked, liquid from bla UNION select 'TOTALS', sum(balance), sum(unlocked), sum(liquid) from bla order by 1 desc;

with base as (
    select 
        wallet_type, 
        sum(balance/1000000) as balance, 
        sum(case 
            when wallet_type = 'N' then balance/1000000 
            when wallet_type = 'C' then 0
            when wallet_type = 'X' then balance
            when unlocked <= (balance/1000000) then unlocked 
            else balance/1000000
            end) as unlocked 
    from accountbalance 
    where (balance/1000000) > 0 
    group by wallet_type
) 
select 
    wallet_type, 
    balance, 
    unlocked 
from base 
UNION 
select 'TOTALS', sum(balance), sum(unlocked) from base order by 3

select id, balance/1000000 as balance, unlocked
from accountbalance
where wallet_type = 'V'
and unlocked > balance/1000000
