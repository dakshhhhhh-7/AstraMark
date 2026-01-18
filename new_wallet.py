from eth_account import Account

acct = Account.create()

print("ADDRESS:", acct.address)
print("PRIVATE_KEY:", acct.key.hex())
