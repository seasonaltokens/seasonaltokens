import pytest
from brownie import TestSpringToken, accounts, chain, reverts, ZERO_ADDRESS

private_key = "0x06e14480eed909feb302ebe7a38075c438fff376d570bdb8ee01b92782804d99"
challenge = b'\xb1zV\xf9t,\x83&\x95\xad\x12\xae\xb4t\xca\x05\xa8&q}:_?\x9dy\x88\x9eL>\xeePk'
nonce = 84870355253201280668639765531949292802255761106050507973491261481313202348862
digest = bytes.fromhex("000001569c7ec7933fa667eca50c0e6b5c7ad4f7465bbef84c3694710d18b2ca")


year = 365 * 24 * 60 * 60
first_era = year * 3 // 4
era = 3 * year

reward_interval = 600
 
initial_reward = 168 * 10**18 
rewards_in_first_era = first_era // reward_interval
rewards_per_era = era // reward_interval

@pytest.fixture
def token(accounts, chain):
    accounts.add(private_key)
    token = accounts[-1].deploy(TestSpringToken)
    token.setChallengeNumber(challenge)
    token.setMiningTarget(token.MAXIMUM_TARGET())
    chain.sleep(1)
    return token

def test_name(token):
    assert token.name() == "Spring Token"

def test_symbol(token):
    assert token.symbol() == "SPRING"

def test_total_supply(token):
    assert token.totalSupply() == token.tokensMinted()
    token.mint(nonce)
    assert token.totalSupply() == token.tokensMinted()

def test_initial_reward(token):
    assert token.INITIAL_REWARD() == 168 * 10**18

def test_get_adjustment_interval(token):
    assert token.getAdjustmentInterval() == reward_interval
    token.setMaxNumberOfRewards(2)
    assert token.getAdjustmentInterval() == 2 * reward_interval
    

def test_initial_difficulty(token):
    assert token.getMiningDifficulty() == (2**256-1) // (token.MAXIMUM_TARGET())

def test_get_mining_reward(token):
    assert token.getMiningReward() == token.INITIAL_REWARD()

def test_mining_reward_halving(token):
    start = token.contractCreationTime()
    assert token._getMiningReward(start) == initial_reward
    assert token._getMiningReward(start + first_era - 1) == initial_reward
    assert token._getMiningReward(start + first_era) == initial_reward / 2
    assert token._getMiningReward(start + first_era + era -1) == initial_reward / 2
    assert token._getMiningReward(start + first_era + era) == initial_reward / 4
    assert token._getMiningReward(start + 205 * year) == 0

def test_number_of_rewards_available(token):
    start = token.contractCreationTime()
    last_reward_time = start + 1
    previous_max_number_of_rewards = 1
    current_time = last_reward_time + 1
    assert token._numberOfRewardsAvailable(last_reward_time, 
                                           previous_max_number_of_rewards,
                                           current_time) == 1
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+600) == 1
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+1199) == 1
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+1200) == 2
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+1799) == 2
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+1800) == 3
    assert token._numberOfRewardsAvailable(last_reward_time, 2, last_reward_time+1800) == 3
    assert token._numberOfRewardsAvailable(last_reward_time, 3, last_reward_time+1800) == 3
    assert token._numberOfRewardsAvailable(last_reward_time, 3, last_reward_time+1) == 3
    assert token._numberOfRewardsAvailable(last_reward_time, 3, last_reward_time+2399) == 3
    assert token._numberOfRewardsAvailable(last_reward_time, 3, last_reward_time+2400) == 4
    assert token._numberOfRewardsAvailable(last_reward_time, 1, last_reward_time+2400) == 4
    assert token._numberOfRewardsAvailable(last_reward_time, 4, last_reward_time+2400) == 4
    assert token._numberOfRewardsAvailable(last_reward_time, 5, last_reward_time+2400) == 5

def test_get_number_of_rewards_available(token):
    start = token.contractCreationTime()
    assert token.getNumberOfRewardsAvailable(start) == 1
    assert token.getNumberOfRewardsAvailable(start + 600) == 1
    assert token.getNumberOfRewardsAvailable(start + 2 * 600) == 2
    assert token.getNumberOfRewardsAvailable(start + 11 * 600) == 11
    token.setMaxNumberOfRewards(2)
    assert token.getNumberOfRewardsAvailable(start) == 2
    token.setMaxNumberOfRewards(3)
    assert token.getNumberOfRewardsAvailable(start) == 3
    assert token.getNumberOfRewardsAvailable(start + 11 * 600) == 11
    token.setMaxNumberOfRewards(300)
    assert token.getNumberOfRewardsAvailable(start) == token.MAX_REWARDS_AVAILABLE()
    txn = token.mint(nonce)
    assert (token.getNumberOfRewardsAvailable(token.lastRewardBlockTime()+1) 
            == txn.events['Mint']['rewardAmount'] / token.INITIAL_REWARD())

def test_number_of_rewards_to_give(token):
    start = token.contractCreationTime()
    last_reward_time = start
    earned = 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 1, start) == 1
    assert token._numberOfRewardsToGive(earned, last_reward_time, 2, start) == 2
    assert token._numberOfRewardsToGive(earned, last_reward_time, 9, start) == 9
    assert token._numberOfRewardsToGive(earned, last_reward_time, 11, start) == 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 20, start) == 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 1, start + 600) == 1
    assert token._numberOfRewardsToGive(earned, last_reward_time, 1, start + 2 * 600) == 2
    assert token._numberOfRewardsToGive(earned, last_reward_time, 1, start + 11 * 600) == 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 1, start + 12 * 600) == 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 2, start + 12 * 600) == 10
    assert token._numberOfRewardsToGive(earned, last_reward_time, 11, start + 11 * 600) == 10

def test_number_of_rewards_to_give_doesnt_exceed_limit(token):
    start = token.contractCreationTime()
    last_reward_time = start
    max_ = token.MAX_REWARDS_AVAILABLE();
    earned = max_
    assert token._numberOfRewardsToGive(earned, last_reward_time, max_, start) == max_
    earned = earned + 1
    assert token._numberOfRewardsToGive(earned, last_reward_time, earned, start) == max_
    
def test_get_reward_amount_for_achieving_target(token):
    start = token.contractCreationTime()
    mining_target = token.getMiningTarget()
    assert token.getRewardAmountForAchievingTarget(mining_target // 1, start) == initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 2, start) == initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 2, 
                                                   start + 2 * 600) == 2 * initial_reward
    token.setMaxNumberOfRewards(2)
    assert token.getRewardAmountForAchievingTarget(mining_target // 1, 
                                                   start + 1 * 600) == 1 * initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 2, 
                                                   start + 1 * 600) == 2 * initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 2, 
                                                   start + 2 * 600) == 2 * initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 3, 
                                                   start + 2 * 600) == 2 * initial_reward
    token.setMaxNumberOfRewards(3)
    assert token.getRewardAmountForAchievingTarget(mining_target // 3, 
                                                   start + 2 * 600) == 3 * initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 3, 
                                                   start + 4 * 600) == 3 * initial_reward
    assert token.getRewardAmountForAchievingTarget(mining_target // 4, 
                                                   start + 40 * 600) == 4 * initial_reward
    token.setMaxNumberOfRewards(1)
    assert token.getRewardAmountForAchievingTarget(mining_target // 4, 
                                                   start + 4 * 600) == 4 * initial_reward

def test_scheduled_number_of_rewards(token):
    creation_time = token.contractCreationTime()
    assert token._scheduledNumberOfRewards(creation_time) == 0
    assert token._scheduledNumberOfRewards(creation_time+599) == 0
    assert token._scheduledNumberOfRewards(creation_time+600) == 1
    assert token._scheduledNumberOfRewards(creation_time+1199) == 1
    assert token._scheduledNumberOfRewards(creation_time+1200) == 2
    assert token._scheduledNumberOfRewards(creation_time+first_era-1) == rewards_in_first_era - 1
    assert token._scheduledNumberOfRewards(creation_time+first_era) == rewards_in_first_era
    assert token._scheduledNumberOfRewards(creation_time+first_era+1) == rewards_in_first_era
    assert token._scheduledNumberOfRewards(creation_time+first_era+era) == (rewards_in_first_era +
                                                                            rewards_per_era)
    assert token._scheduledNumberOfRewards(creation_time+first_era+2*era-1) == (rewards_in_first_era +
                                                                                2 * rewards_per_era - 1)
    assert token._scheduledNumberOfRewards(creation_time+first_era+2*era) == (rewards_in_first_era +
                                                                              2 * rewards_per_era)
    assert token._scheduledNumberOfRewards(creation_time+first_era+2*era+1) == (rewards_in_first_era +
                                                                                2 * rewards_per_era)
    assert token._scheduledNumberOfRewards(creation_time+first_era+60*era+1) == (rewards_in_first_era +
                                                                                 60 * rewards_per_era)

def test_increase_difficulty(token, chain):
    start = token.contractCreationTime()
    token.setMiningTarget(2**233)
    initial_target = token.getMiningTarget()
    chain.sleep(int(0.5 * reward_interval))
    last_reward_time = start
    token.setMiningTarget(token._adjustDifficulty(initial_target, last_reward_time, 
                                                  1, chain.time()))
    assert token.getMiningTarget() < initial_target
    assert token.getMiningTarget() == (initial_target * 99) // 100

def test_increase_difficulty_to_limit(token, chain):
    start = token.contractCreationTime()
    token.setMiningTarget(2**233)
    initial_target = token.getMiningTarget()
    chain.mine()
    for i in range(36):
        last_reward_time = chain.time()
        chain.sleep(int(0.5 * reward_interval))
        token.setMiningTarget(token._adjustDifficulty(token.getMiningTarget(), last_reward_time, 1, chain.time()))
    assert token.getMiningTarget() != token.MINIMUM_TARGET()
    last_reward_time = chain.time()
    chain.sleep(int(0.5 * reward_interval))
    token.setMiningTarget(token._adjustDifficulty(token.getMiningTarget(), last_reward_time, 1, chain.time()))
    assert token.getMiningTarget() == token.MINIMUM_TARGET()

def test_decrease_difficulty(token, chain):
    start = token.contractCreationTime()
    token.setMiningTarget(2**233)
    initial_target = token.getMiningTarget()
    chain.sleep(int(1.5 * reward_interval))
    last_reward_time = start
    token.setMiningTarget(token._adjustDifficulty(initial_target, last_reward_time, 1, chain.time()))
    assert token.getMiningTarget() > initial_target
    assert token.getMiningTarget() == (initial_target  * 100) // 99

def test_decrease_difficulty_multiple_rewards(token, chain):
    start = token.contractCreationTime()
    token.setMiningTarget(2**233)
    initial_target = token.getMiningTarget()
    chain.sleep(int(2.5 * reward_interval))
    last_reward_time = start
    token.setMiningTarget(token._adjustDifficulty(initial_target, last_reward_time, 2, chain.time()))
    assert token.getMiningTarget() > initial_target
    assert token.getMiningTarget() == (initial_target * 100) // 99

def test_decrease_difficulty_to_limit(token, chain):
    start = token.contractCreationTime()
    token.setMiningTarget(2**234-1)
    last_reward_time = start
    initial_target = token.getMiningTarget()
    chain.sleep(int(2.5 * reward_interval))
    token.setMiningTarget(token._adjustDifficulty(initial_target, last_reward_time, 1, chain.time()))
    assert token.getMiningTarget() == token.MAXIMUM_TARGET()

def test_reward_era(token):
    start = token.contractCreationTime()
    assert token.rewardEra(start) == 0
    assert token.rewardEra(start + first_era - 1) == 0
    assert token.rewardEra(start + first_era) == 1
    assert token.rewardEra(start + first_era + era - 1) == 1
    assert token.rewardEra(start + first_era + era) == 2

def test_minting(token):
    txn = token.mint(nonce)
    assert txn.events['Mint']['rewardAmount'] == token.INITIAL_REWARD()

def test_legacy_minting(token):
    txn = token.mint(nonce, digest)
    assert txn.events['Mint']['rewardAmount'] == token.INITIAL_REWARD()

def test_revert_legacy_minting(token):
    with reverts("Challenge digest does not match expected digest on token contract"):
        token.mint(nonce+1, digest)

def test_revert_zero_reward(token):
    chain.sleep(205 * year)
    token.mint(nonce)
    token.setChallengeNumber(challenge)
    with reverts("Reward has reached zero"):    
        txn = token.mint(nonce)

def test_revert_digest_above_mining_target(token):
    token.setMiningTarget(2**205)
    with reverts():
        txn = token.mint(nonce)

def test_tokens_minted(token):
    assert token.tokensMinted() == 0
    token.mint(nonce)
    assert token.tokensMinted() == initial_reward

def test_challenge_number_changes(token):
    token.setChallengeNumber(challenge)
    assert token.getChallengeNumber() == "0x"+challenge.hex()
    token.mint(nonce)
    assert token.getChallengeNumber() != "0x"+challenge.hex()



@pytest.fixture
def token_with_balance(token):
    token.mint(nonce)
    return token


def test_balance(token_with_balance, accounts):
    assert token_with_balance.balanceOf(accounts[-1]) == token_with_balance.INITIAL_REWARD()

def test_transfer(token_with_balance, accounts):
    token_with_balance.transfer(accounts[0], 10)
    assert token_with_balance.balanceOf(accounts[0]) == 10

def test_revert_transfer_to_zero_address(token_with_balance):
    with reverts():
        token_with_balance.transfer(ZERO_ADDRESS, 10)

def test_revert_insufficient_balance(token_with_balance, accounts):
    with reverts():
        token_with_balance.transfer(accounts[0], token_with_balance.INITIAL_REWARD() + 1)

def test_approve(token_with_balance, accounts):
    token_with_balance.approve(accounts[0], 10)
    assert token_with_balance.allowance(accounts[-1], accounts[0]) == 10

def test_revert_approve_zero_address(token_with_balance, accounts):
    with reverts():
        token_with_balance.approve(ZERO_ADDRESS, 10)

def test_revert_approve_contract_address(token_with_balance, accounts):
    with reverts():
        token_with_balance.approve(token_with_balance.address, 10)

def test_safe_approve(token_with_balance, accounts):
    token_with_balance.safeApprove(accounts[0].address, 0, 10)
    assert token_with_balance.allowance(accounts[-1], accounts[0]) == 10

def test_revert_safe_approve(token_with_balance, accounts):
    with reverts("Current spender allowance does not match specified value"):
        token_with_balance.safeApprove(accounts[0], 1, 10)



@pytest.fixture
def token_with_allowance(token_with_balance, accounts):
    token_with_balance.approve(accounts[0], 10)
    return token_with_balance


def test_transferFrom(token_with_allowance, accounts):
    token_with_allowance.transferFrom(accounts[-1], accounts[1], 10, {'from': accounts[0]})
    assert token_with_allowance.balanceOf(accounts[1]) == 10

def test_revert_transferFrom_zero_address(token_with_allowance):
    with reverts():
        token_with_allowance.transferFrom(accounts[-1], ZERO_ADDRESS, 10, {'from': accounts[0]})

def test_revert_transferFrom_contract_address(token_with_allowance, accounts):
    with reverts():
        token_with_allowance.transferFrom(accounts[-1], token_with_allowance.address, 10, 
                                          {'from': accounts[0]})

def test_revert_insufficient_allowance(token_with_allowance, accounts):
    with reverts():
        token_with_allowance.transferFrom(accounts[-1], accounts[1], 11, {'from': accounts[0]})

def test_revert_transferFrom_insufficient_balance(token_with_allowance, accounts):
    token_with_allowance.approve(accounts[0], token_with_allowance.INITIAL_REWARD() + 1)
    with reverts():
        token_with_allowance.transferFrom(accounts[-1], accounts[1], 
                                          token_with_allowance.INITIAL_REWARD() + 1, 
                                          {'from': accounts[0]})

def test_revert_transferFrom_overflow(token_with_allowance, accounts):
    huge_number = 2 * (2**255-1)
    token_with_allowance.setBalance(accounts[-1], huge_number)
    token_with_allowance.setBalance(accounts[1], huge_number)
    token_with_allowance.approve(accounts[0], huge_number)
    with reverts("Integer overflow"):
        token_with_allowance.transferFrom(accounts[-1], accounts[1], 
                                          huge_number, 
                                          {'from': accounts[0]})

def test_approve_and_call_fallback(token_with_allowance):
    assert token_with_allowance.notifiedAllowance() == 0
    token_with_allowance.approveAndCall(token_with_allowance.address, 10, 1)
    assert token_with_allowance.notifiedAllowance() == 10

def test_approve_and_call_fallback_revert_zero_address(token_with_allowance):
    with reverts("Invalid address"):
        token_with_allowance.approveAndCall(ZERO_ADDRESS, 10, 1)

def test_safe_approve_and_call_fallback(token_with_allowance):
    assert token_with_allowance.notifiedAllowance() == 0
    token_with_allowance.safeApproveAndCall(token_with_allowance.address, 0, 10, 1)
    assert token_with_allowance.notifiedAllowance() == 10

def test_revert_safe_approve_and_call_fallback(token_with_allowance):
    assert token_with_allowance.notifiedAllowance() == 0
    with reverts():
        token_with_allowance.safeApproveAndCall(token_with_allowance.address, 1, 10, 1)
    
def test_transfer_any_erc20_token(token_with_allowance, accounts):
    token_with_allowance.transfer(token_with_allowance.address, 100)
    token_with_allowance.setBalance(accounts[-1], 0)
    assert token_with_allowance.balanceOf(accounts[-1]) == 0
    assert token_with_allowance.balanceOf(token_with_allowance.address) == 100
    token_with_allowance.transferAnyERC20Token(token_with_allowance.address, 100)
    assert token_with_allowance.balanceOf(token_with_allowance.address) == 0
    assert token_with_allowance.balanceOf(accounts[-1]) == 100
