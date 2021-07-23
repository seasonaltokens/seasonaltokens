import pytest
from brownie import TestSpringToken, accounts, chain, reverts, ZERO_ADDRESS
from math import log, sin, exp
from random import random

private_key = "0x06e14480eed909feb302ebe7a38075c438fff376d570bdb8ee01b92782804d99"
challenge = b'\xb1zV\xf9t,\x83&\x95\xad\x12\xae\xb4t\xca\x05\xa8&q}:_?\x9dy\x88\x9eL>\xeePk'
nonce = 84870355253201280668639765531949292802255761106050507973491261481313202348862
digest = bytes.fromhex("000001569c7ec7933fa667eca50c0e6b5c7ad4f7465bbef84c3694710d18b2ca")


year = 365 * 24 * 60 * 60
first_era = year * 3 // 4
era = 3 * year

reward_interval = 600
MAXIMUM_TARGET = 2**234
MINIMUM_TARGET = 2**16

REWARD_INTERVAL = 600
 
initial_reward = 168 * 10**18 
rewards_in_first_era = first_era // reward_interval
rewards_per_era = era // reward_interval

time_limit = 2 * year

@pytest.fixture
def token(accounts, chain):
    accounts.add(private_key)
    token = accounts[-1].deploy(TestSpringToken)
    token.setChallengeNumber(challenge)
    #token.setMiningTarget(token.MAXIMUM_TARGET())
    chain.sleep(1)
    return token

def _adjustDifficulty(_miningTarget, _lastRewardBlockTime, rewardsGivenNow, t):
    timeSinceLastReward = t - _lastRewardBlockTime
    if (timeSinceLastReward * 88 < rewardsGivenNow * reward_interval * 61):
        _miningTarget = (_miningTarget // 100) * 99

    elif (timeSinceLastReward * 88 > rewardsGivenNow * reward_interval * 61):
        _miningTarget = (_miningTarget // 99) * 100
        
    if (_miningTarget < MINIMUM_TARGET):
        _miningTarget = MINIMUM_TARGET
    
    if (_miningTarget > MAXIMUM_TARGET):
        _miningTarget = MAXIMUM_TARGET

    return _miningTarget

def constant_hashpower(t):
    return 1e8

def oscillating_hashpower(t):
    return constant_hashpower(t) * (1 + 0.5 * sin(t * 12 * 6.28 / year))

def increasing_hashpower(t):
    return constant_hashpower(t) * exp(t / year)

def decreasing_hashpower(t):
    return constant_hashpower(t) * exp(-0.1 * t / year)

def interval(rate):
    return -log(random()) / rate

def get_mining_intervals(token, hashpower_function):
    mining_target =  token.getMiningTarget()
    t, rewards, time_counted, intervals  = 0, 0, 0, []
    while t < time_limit:
        rate = hashpower_function(t) * mining_target / 2**256
        intervals.append(interval(rate))
        mining_target = _adjustDifficulty(mining_target, t , 1, t+intervals[-1])
        t += intervals[-1]
        time_counted += intervals[-1]
        rewards += 1
    return intervals


def test_mean_interval_equals_ten_minutes_constant_hashpower(token, chain):
    intervals = get_mining_intervals(token, constant_hashpower)
    assert abs((sum(intervals) / len(intervals)) / 600. - 1) < .015


def test_mean_interval_equals_ten_minutes_oscillating_hashpower(token, chain):
    intervals = get_mining_intervals(token, oscillating_hashpower)
    assert abs((sum(intervals) / len(intervals)) / 600. - 1) < .015


def test_mean_interval_equals_ten_minutes_increasing_hashpower(token, chain):
    intervals = get_mining_intervals(token, increasing_hashpower)
    assert abs((sum(intervals) / len(intervals)) / 600. - 1) < .015


def test_mean_interval_equals_ten_minutes_decreasing_hashpower(token, chain):
    intervals = get_mining_intervals(token, decreasing_hashpower)
    assert abs((sum(intervals) / len(intervals)) / 600. - 1) < .015


