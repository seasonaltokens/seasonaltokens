from brownie import SummerToken, accounts

def main():
    acct = accounts.load('deployment')
    SummerToken.deploy({'from': acct})
