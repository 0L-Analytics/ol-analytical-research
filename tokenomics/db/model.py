import os
import re
from sqlalchemy import Column, DateTime, Integer, String, func, Float, BigInteger, or_
from sqlalchemy.sql.expression import label, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr
from datetime import datetime

from . import engine, session
# from ol_util import lookup_unlocked


Base = declarative_base()


# class PaymentEvent(Base):
#     __tablename__ = "paymentevent"

#     id = Column(Integer, primary_key=True)
#     address = Column(String(100), nullable=False)
#     amount = Column(Float, nullable=False, default=0)
#     currency = Column(String(16), nullable=False)
#     _metadata = Column(String(100), nullable=False)
#     sender = Column(String(100))
#     recipient = Column(String(100))
#     type = Column(String(100), nullable=False)
#     transactionkey = Column(String(100))
#     seq = Column(Integer, nullable=False)
#     height = Column(Integer, nullable=False, default=0)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# class AccountTransaction(Base):
#     __tablename__ = "accounttransaction"

#     id = Column(Integer, primary_key=True)
#     address = Column(String(100), nullable=False)
#     sequence_number = Column(Integer, nullable=False)
#     version = Column(Integer, nullable=False)
#     tx = Column(JSONB, nullable=False)
#     hash = Column(String(64), nullable=False)
#     vm_status = Column(JSONB)
#     gas_used = Column(Integer, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AccountBalance(Base):
    __tablename__ = "accountbalance"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False, unique=True)
    account_type = Column(String(100), nullable=False)
    balance = Column(BigInteger, nullable=False)
    unlocked = Column(BigInteger, nullable=True)
    wallet_type = Column(String(1), nullable=False, default='X')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def lookup_wallet_type(address: AnyStr) -> AnyStr:
        """
        Checks if a given address is a slow wallet.
        :param address: the address to check
        :return: 'S' > Slow, 'C' > Community, 'O' > Other
        """
        # We are checking both 'SlowWallet' and 'Community' occurence in the query output
        with os.popen(f"ol -a {address} query -r | sed -n '/SlowWallet/,/StructTag/p'") as f:
            for elem in f.readlines():
                if 'SlowWallet' in elem:
                    return 'S'
        return 'N'

    def lookup_unlocked(address: AnyStr) -> int:
        """
        Checks if a given address is a slow wallet.
        :param address: the address to check
        :return: 
        """        
        amt = 0

        # We are checking both 'SlowWallet' and 'Community' occurence in the query output
        with os.popen(f"ol -a {address} query -u") as f:
            for line in f.readlines():
                if re.search("(UNLOCKED)", line):
                    # print(f"line={line}")
                    amt = int(int(line.split(' ')[2]) / 1000000)
        return amt

    def lookup_wallets_unlocked(self) -> None:
        wallets = session\
            .query(AccountBalance)\
            .filter(
                AccountBalance.balance > 0, AccountBalance.wallet_type == 'S')\
            .all()
        for v in wallets:
            v.unlocked = self.lookup_unlocked(v.address)
        session.commit()
    
    def lookup_wallet_types(self) -> None:
        validators = session\
            .query(AccountBalance)\
            .filter(
                AccountBalance.balance > 0,
                or_(AccountBalance.account_type == 'basic', 
                    AccountBalance.account_type == 'miner'))\
            .all()
        for v in validators:
            v.wallet_type = self.lookup_wallet_type(v.address)
            print(f"{v.address} > {v.wallet_type}")
        session.commit()

    def upload_balances(balance_list: List) -> None:
        try:
            # Iterate objects and store them in the db
            for pe_obj in balance_list:
                pe_id = session\
                    .query(AccountBalance.id)\
                    .filter(AccountBalance.address == pe_obj['address'])\
                    .scalar()

                o = AccountBalance(
                    address=pe_obj['address'],
                    balance=int(pe_obj['balance']),
                    account_type=pe_obj['account_type']
                )

                if pe_id:
                    o.id = pe_id
                    session.merge(o)
                else:
                    session.add(o)

            session.commit()
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")


# ALTER TABLE accountbalance ADD COLUMN wallet_type CHAR(1);

# Base.metadata.create_all(engine)
