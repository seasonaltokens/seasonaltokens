from brownie import AutumnToken, accounts

def main():
    acct = accounts.load('deployment')
    AutumnToken.deploy({'from': acct})
