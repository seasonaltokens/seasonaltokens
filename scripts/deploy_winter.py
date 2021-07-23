from brownie import WinterToken, accounts

def main():
    acct = accounts.load('deployment')
    WinterToken.deploy({'from': acct})
