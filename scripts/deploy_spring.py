from brownie import SpringToken, accounts

def main():
    acct = accounts.load('deployment')
    SpringToken.deploy({'from': acct})
