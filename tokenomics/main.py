from ol_util import (
    load_account_balances_for_acc_type,
    lookup_wallet_type
)
from db.model import session, AccountBalance, label, cast, Integer, or_
from typing import List, Dict, Tuple
from collections import namedtuple
from datetime import datetime
from time import mktime
from json import dumps
from db.config import Config


def lookup_slow_flag(address_list: List) -> None:
    counter = 0
    for addr_obj in address_list:
        counter += 1
        print(f"Checking [{counter}] {addr_obj['address']}")
        id = session\
            .query(AccountBalance.id)\
            .filter(AccountBalance.address == addr_obj['address'])\
            .scalar()
        if addr_obj['account_type'] == 'community':
            addr_obj['wallet_type'] = 'C'
        else:
            addr_obj['wallet_type'] = lookup_wallet_type(addr_obj['address'])
        
        ab = AccountBalance(
            id=id,
            wallet_type=addr_obj['wallet_type']
        )

        session.merge(ab)
        session.commit()
    
    return None


def get_acc_balances() -> List:
    qres = session.query(
        AccountBalance.id,
        AccountBalance.address,
        AccountBalance.account_type,
        label("balance", cast(AccountBalance.balance / 1000000, Integer)),
        AccountBalance.updated_at)\
            .filter(AccountBalance.wallet_type=='X')\
            .all()
    list_out = []
    for ab in qres:
        obj = {
            "id": ab[0],
            "address": ab[1],
            "account_type": ab[2],
            "balance": ab[3],
            "updated_at": mktime(ab[4].timetuple()),
        }
        list_out.append(obj)
    return list_out


def how_liquid_are_we() -> None:
    # print("getting validator balance...")
    # load_account_balances_for_acc_type("validator")
    print("getting unlocked balances")
    AccountBalance.lookup_wallets_unlocked(AccountBalance)
    # print("getting miner balances")
    # load_account_balances_for_acc_type("miner")
    # print("getting basic balances")
    # load_account_balances_for_acc_type("basic")
    # print("getting community balances")
    # load_account_balances_for_acc_type("community")
    # print("lookup wallet types slow / normal")
    # AccountBalance.lookup_wallet_types(AccountBalance)
    # # # # print("calculate liquidity...")
    # # # # ls = AccountBalance.get_liquid_supply()
    # # # # print(f"We have a liquid supply of {ls[0]} / {ls[1]}")

    print("done!")


def main():
    ...
    # account_balance_list = get_acc_balances()
    # lookup_slow_flag(account_balance_list)
    # Serializing json
    # json_object = dumps(account_balance_list_rich, indent=4)
    
    # # Writing to sample.json
    # with open(f"{Config.PYTHONPATH}/assets/generated/wallet_balances.json", "w") as outfile:
    #     outfile.write(json_object)


if __name__ == "__main__":
    how_liquid_are_we()
