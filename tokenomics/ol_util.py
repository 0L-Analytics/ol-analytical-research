import os
import re
from typing import AnyStr
from config import Config
from datetime import datetime
from typing import List, AnyStr
from requests import get
from db.model import session, AccountBalance


def get_0l_api_data(end_point_suffix: AnyStr, output_elem: AnyStr=None, **options) -> List:
    """
    Gets data from the 0L API.
    :param end_point_suffix: the path of the endpoint at 0lexplorer.io
    :param output_elem: the child element in the output dictionary to be returned, if applicable
    :param options: options to be passed along with API call
    :return: list of elements representing a data set
    """
    try:
        option_string = ""
        if len(options) > 0 and end_point_suffix[1:]:
            for option_key in options.keys():
                if len(option_string) > 0:
                    option_string += "&"
                option_string += f"{option_key}={options[option_key]}"

        api_url = f"{Config.BASE_API_URI}{end_point_suffix}{option_string}"
        result = get(api_url, timeout=300).json()
        if output_elem and output_elem in result:
            result = result[output_elem]
    except Exception as e:
        print(f"[{datetime.now()}]:{e}")
        result = []
    return result


def load_account_balances_for_acc_type(account_type: AnyStr) -> None:
    """
    Loads balances for an address list into the db.
    :param address_list: list of 0L addresses
    :return: no return value
    """
    # fetch balances
    try:           
        # Get the data from the api
        result = get_0l_api_data(
            end_point_suffix=f":444/balances?account_type={account_type}"
        )

        if result and len(result) > 0:
            AccountBalance.upload_balances(result)

    except Exception as e:
        print(f"[{datetime.now()}]:ERROR:{e}")


if __name__ == "__main__":
    print(AccountBalance.lookup_unlocked("7e56b29cb23a49368be593e5cfc9712e"))
    
    # test_list = [
    #     "5F8AC83A9B3BF2EFF20A6C16CD05C111", # SLOW basic wallet
    #     "2BFD96D8A674A360B733D16C65728D72", # normal basic wallet
    #     "1367B68C86CB27FA7215D9F75A26EB8F", # SLOW community wallet
    #     "5335039ab7908dc38d328685dc3b9141", # normal miner wallet
    #     "7e56b29cb23a49368be593e5cfc9712e", # SLOW validator wallet
    #     "82a1097c4a173e7941e2c34b4cbf15b4", # normal miner wallet
    #     "5e358589da97d5f08bf3a7462a112ae6", # normal miner wallet
    #     "19E966BFA4B32CE9B7E23721B37B96D2", # SLOW another community wallet
    #     "cd0fa23141e9e5e348b33c5da51f211d", # normal miner wallet
    #     "f100a2878d61bab8554aed256feb8001", # normal miner wallet
    #     "4be425e5306776a0bd9e2db152b856e6", # SLOW miner wallet
    #     "7103da7bb5bb15eb7e72b6db16147f56", # normal miner wallet
    #     "74745f89883134d270d0a57c6c854b4b", # normal miner wallet
    # ]

    # for addr in test_list:
    #     if lookup_wallet_type(addr) == 'S':
    #         print(f"{addr} is a slow wallet!")
    #     elif lookup_wallet_type(addr) == 'C':
    #         print(f"{addr} is a community wallet!")
    #     else:
    #         print(f"{addr} is a normal wallet!")
    