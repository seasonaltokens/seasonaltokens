# Seasonal Tokens

### Abstract

Many agricultural commodities exhibit seasonality in their prices, meaning that they are predictably more expensive at certain times of the year than at other times. This is often due to the fact that the commodities are naturally produced in greater quantities at specific times, such as harvest seasons, which are not under anybody's control. Cryptocurrency coins and tokens whose rates of production are halved at regular intervals also display seasonality in their prices. A few months after bitcoin's rate of production is halved, the price rises as the market adjusts to the new scarcity of the coin. Unlike agricultural commodities, the production schedule, and the consequent seasonality, of cryptocurrencies, is specified by the coin's code, and can be chosen to produce desired effects. This makes it possible to have multiple coins or tokens whose prices will predictably rise, one after another, so that investors can hold a coin while it is rising in price, and then trade it for greater quantities of a cheaper coin that will rise in price next. Here we introduce four mineable tokens, Spring, Summer, Autumn and Winter, each of which has a rate of production that halves every three years, with a nine month interval between the halving of each token and the halving of the next token. This creates a predictable cyclical variation of the relative prices of the four tokens, allowing an investor to continually increase the total number of tokens they hold by trading each token for the next one in the cycle every nine months.


## Introduction

Every four years, the rate of production of bitcoin is cut in half, and in the following months, a scarcity of bitcoin accumulates in comparison to the previous equilibrium, which eventually forces the price to rise as fewer bitcoins become available to buy on the markets. This has made bitcoin a very profitable investment, but the price rises in this way only once every four years, taking about a year to increase from the previous equilibrium price to a new peak. After that, the price tends to decrease for a period of several months to a year, after the market's expectation of rising prices is replaced by an expectation of falling prices. A new equilibrium price emerges during the following years, when the supply has been stable for years and there are no more expectations of rising or falling prices. That equilibrium is then disturbed by the next cut in the rate of production, which repeats the pattern.
 
This rise in price due to increasing scarcity is a desirable property for an investment, but it would be preferable to have an investment that always increases in value, rather than increasing, decreasing, and then stabilizing over the course of many years. When the bitcoin price begins to fall from its new peak, it would be desirable to be able to exchange bitcoins for another coin that's just beginning to rise in price as a consequence of its rate of production getting cut in half.

The four tokens introduced here have scheduled production halvings that occur, for each token, nine months after the previous token's halving. This allows investors to hold a coin while it is rising in value, and then trade it for a coin that will rise in value during the subsequent months. An investor who follows this strategy will always hold a token that has recently become scarce in comparison to what the market has become accustomed to, and whose price can be expected to rise as the market adjusts to the new scarcity.

Each token will have a total supply of approximately 33,112,800 tokens. So in the very long term, the coins can be expected to have approximately equal value. However, at any given time before then, one token will be generated at a faster rate than the others, and over time will tend to become cheaper to buy. Another token, which was previously generated at the fastest rate, will have recently halved its rate of production, and will then be generated at the slowest rate of the four, and will become scarcer, and consequently more expensive, over time. Trading the more expensive tokens for the cheaper ones will allow an investor to increase the number of tokens that he or she owns over time.

An investor who holds 1 Spring Token, for example, can wait until the rate of production of Spring Tokens is halved, and then the Summer Token will be the one that is produced at the highest rate. This will eventually cause the Summer Token to become cheaper than the Spring Token, whose newfound scarcity will make it more expensive. The investor may be able to trade the 1 Spring Token for 1.5 Summer Tokens. Those 1.5 Summer Tokens might later be traded for 2  Autumn Tokens, and those in turn might later be traded for 2.5 Winter Tokens.

The cycle completes when the Winter Tokens are traded for Spring Tokens again, and the investor may at that time be able to buy 3 Spring Tokens, and can repeat the cyclical process to acquire more.

 
## Production Schedules

Tokens are issued as rewards for mining. A reward for each token is paid out every ten minutes on average. The number of tokens in each reward differs for the four tokens and decreases with every halving event. The Spring Token is initially produced at the fastest rate, but has the earliest halving. One fifth of the total supply of Spring Tokens will be mined before its first halving. One third of the total supply of Summer Tokens, three sevenths of the total supply of Autumn tokens, and one half of the total supply of Winter Tokens, will be mined before the first halvings of those tokens.
 
![supply schedule](supply_curves.png)<br>
*Figure 1. The total number of mined tokens of each type as a function of time.*

&nbsp;

Figure 1 above shows the total number of tokens mined over time for each of the four tokens. Although they are produced at different rates at any given time, every three years the quantities existing become equal. In the long term, all four curves approach 33,112,800.


![production schedule](reward_curves.png)<br>
*Figure 2. The number of tokens per reward over time.*

&nbsp;

The rate of production of each token over time is shown in figure 2. The initial reward amounts are 168, 140, 120 and 105 tokens, for the Spring, Summer, Autumn and Winter tokens respectively. These rewards are halved every three years. Quantities of each token are specified with 18 decimal places of precision. No more tokens will be mined after the size of the reward drops below the minimum representable quantity, which will happen in approximately 200 years.


![scarcity](scarcity_curves.png)<br>
*Figure 3. The scarcity of each token over time, modelled as the fraction by which the number of tokens generated in the last 6 months is smaller than the number generated in the previous 6 months.*

&nbsp;

The price of coins tends to rise a number of months after a halving takes place, as the accumulating scarcity of coins, in comparison to what the market has become used to, becomes large enough to affect the price. We can take the number of tokens produced between six months and a year ago as an indicator of the six-month supply that the market has adjusted to.
The actual number produced in the last six months may be as little as half of that, in which case the previous equilibrium between supply and demand will become unsustainable, and the price will need to increase to find a new equilbrium.

As figure 3 shows, the tokens become scarce one after another, cyclically. The market price of each token will adjust to that token's scarcity when it appears, and so the tokens will tend to rise in price, one after another, in a predictable sequence.


## Implementation

The tokens are ERC20 tokens issued on the Ethereum blockchain. The code was forked from the 0xBitcoin project, which implements a mineable token with a decreasing rate of production. The production schedule was adjusted to create each of the four seasonal tokens. As ERC20 tokens, the seasonal tokens can be traded permissionlessly on decentralized exchanges, stored on standard hardware wallets, received and sent with the Metamask plugin, and viewed on etherscan.io.

The tokens also comply with the ERC-918 standard for mineable tokens. This provides a standardized interface for applications to interact with tokens that can be mined. Existing mining software for 0xBitcoin and similar coins can automatically be used to mine the seasonal tokens.


## Mining

The tokens are mined using the proof-of-work algorithm for ERC20 tokens introduced by 0xBitcoin, using the `Keccak` hashing algorithm. To earn a reward, a miner must find a nonce that solves the equation:

	Keccak(challenge, ethereum_address, nonce) < mining_target

where `ethereum_address` is the address to which the reward will be given, the challenge is:

	challenge = latest_ethereum_block_hash XOR total_tokens_mined XOR token_identifier

and `token_identifier` is a different number for each of the four tokens. The inclusion of the latest ethereum block hash in the challenge ensures that the challenge will change to something unpredictable after each reward is mined in a new ethereum block. This is xored with the total number of tokens mined so that, in the unlikely event that multiple mint transactions occur within a single ethereum block, the challenge will change even though the latest ethereum block hash is the same. The inclusion of the token identifier ensures that different work needs to be done to mine the different tokens. This is necessary to allow the tokens to have independent market prices, with one token possibly being worth a lot more work than another.


## Batching Rewards to Reduce Gas Costs

Users must pay to consume computational resources on the ethereum network. Every interaction with a smart contract, such as those that implement the seasonal tokens, uses up a certain amount of gas, which measures how much work the network must do to process it. When demand for these resources is high, users are willing to pay more to have their transactions processed, and the price of gas rises.

Miners use their own hardware to perform the work necessary to mine the seasonal tokens, but to submit the resulting proof-of-work to the ethereum network, the miner must pay for the gas used by the smart contract, which checks the proof and issues the tokens. The amount of gas required for this is predictable, but the price of that gas depends on how busy the network is at the time.

This can lead to a situation in which the cost of submitting the transaction that claims the tokens exceeds the value of the tokens mined. When this happens, miners will stop mining because they lose money every time they earn a reward. 

To prevent this from happening, the smart contracts that receive the proofs of work allow miners to receive multiple rewards in a single transaction, by submitting a nonce that proves that the miner has done enough work to earn that many rewards. In the simplified scenario in which only a single miner is mining a particular token, that miner can claim 10 rewards, consisting of, for example, 1,680 Spring Tokens, once every hundred minutes instead of one reward of 168 tokens every ten minutes. By doing this, the miner can reduce the amount of gas used by a factor of ten.

This mechanism ensures that gas costs won't make mining unprofitable. The fraction of the miner's earnings spent on gas can be made as low as needed for profitable mining to continue, up to a limit of 72 rewards per batch. This limit is needed to ensure that the rewards are claimed frequently enough to allow the mining difficulty to adjust to the hashrate.

Miners claim rewards by calling the smart contract's `mint` function, providing it with a nonce that satisfies:

	hash = Keccak(challenge, ethereum_address, nonce) < mining_target

The contract keeps track of a parameter called `max_rewards_per_mint`, and the number of rewards given to a miner in a single `mint` operation is:

	minimum(int(mining_target/hash), max_rewards_per_mint)

This is a fair amount to pay the miner. It takes twice as much work, on average, to find a hash that satisfies `mining_target/hash > 2` than it does to find a hash that satisfies `mining_target/hash > 1`. 

However, the hashes produced by the `Keccak` function are essentially random numbers, and when a miner finds a hash lower than `mining_target`, it is equally likely to be above `mining_target/2` or below it. The intention is to reward miners in proportion to the amount of work they do, not in proportion to how lucky they are, so the value of `max_rewards_per_mint` is intentionally kept as low as possible, while allowing mining to continue.

When most miners are willing to accept a single reward in a `mint` operation, the value of `max_rewards_per_mint` is kept at 1. But if enough time passes without any miner claiming a reward, this may mean that it is not profitable to claim a single reward, and `max_rewards_per_mint` increases to 2, and continues to increase until a reward is claimed or the limit of 72 is reached.

If `max_rewards_per_mint = N` and a miner presents a hash that claims `M` rewards, with `M < N`, then `max_rewards_per_mint` decreases to `M`. This ensures that, when gas prices fall, the number of rewards that can be minted at once will decrease to the level at which miners continue to submit claims.

A malicious miner who deliberately sets `max_rewards_per_mint` to a value lower than the minimum profitable number of rewards must suffer a loss when doing so, and cannot significantly inconvenience other miners by forcing them to wait for it to rise again, because the amount of waiting time needed is equal to the number of rewards multiplied by 10 minutes, which is the same as the mean interval between the `mint` operations of the honest miners. 

The miners who need a minimum payout of `N` rewards can continue to mine when `max_rewards_per_mint` is below `N`. If they find a nonce before it can be profitably submitted, they can switch to mining one of the other three tokens until then. If gas prices rise suddenly, there may be no token that's currently profitable to submit a `mint` operation for, but an individual miner is extremely unlikely to have found nonces for all four that will be profitable to submit in due time. Miners will always have work to do.

Miners can know how many rewards they can currently claim by querying the smart contract, using the `getNumberOfRewardsAvailable` function, which returns the value of `max_rewards_per_mint`. Miners can also call the `getRewardAmountForAchievingTarget` function, which returns the number of tokens that they will be awarded for submitting a hash with a value lower than a specified target value at a specified time. By comparing this number to the market price of the tokens and the cost of gas, a miner can determine whether it's profitable to submit a solution or not.


## Difficulty Adjustments

The difficulty of mining the seasonal tokens is adjusted to keep the mean interval between rewards close to 10 minutes. This is achieved by keeping the median interval close to 10 minutes multiplied by log(2). 

Specifically, the mining target is decreased by 1% when the interval between one successful mining event and the next is less than log(2) multiplied by 10 minutes multiplied by the number of rewards issued, and it is increased by 1% when the interval is greater than this.

This keeps the total rate of production of the tokens close to the target rate of 1 reward every 10 minutes, regardless of the overall mining power and the cost of gas relative to the price of the tokens. 


## Reward Halvings

The reward halvings occur on schedule, at their specified times, instead of after a specific number of rewards or tokens have been issued. This prevents the times of the halvings from deviating from the schedule due to a shortfall or excess in the total number of tokens produced. However, it means that there will be small deviations of the number of tokens produced from the scheduled amount. The total number of tokens produced by the time a halving occurs may be slightly ahead of schedule or behind schedule. The halving will occur on time anyway.

Because of this, the total supply of 33,118,200 tokens is an estimate based on the hypothesis that exactly one reward will be paid out every 10 minutes. In practice, the rate will be close to this value but not exactly equal to it.


## Disclaimer

This white paper exists to document the purpose and defining features of the tokens described. It is not investment advice. No statement or combination of statements made in this document constitutes investment advice, a promise of any kind, or a guarantee of future prices. The authors make no such guarantees and will not be responsible for any investment losses suffered by anybody using the tokens. The tokens are not securities. They do not secure anything. They are not redeemable for anything else and they are not accompanied by any promise. They are simply mineable, tradeable tokens with specific production schedules. There is no guarantee that they will rise in price over time.

The acquisition of a token by a person does not establish any legal contract between that person and any other person, and it does not create any legal obligations that any other person must comply with. The code that controls the creation and transfer of tokens is visible to everyone and is not under anybody's control. It operates automatically. What it will do in any circumstance can be understood by anybody who reads the code and understands it completely. This document explains what the code is intended to do, but provides no guarantee. Users of the tokens should be aware of their responsibility to understand the technology for themselves. Users must be aware that nobody has given them any guarantees and nobody is liable for their losses in the event that something goes wrong.

Investors who rely on the judgement of others for their investment decisions should not use these tokens.


## References

Nakamoto, Satoshi, 2008. *"Bitcoin: A Peer-to-Peer Electronic Cash System"*.
<br>
	https://nakamotoinstitute.org/bitcoin/

Buterin, Vitalik, 2013. *"Ethereum Whitepaper"*.
<br>
	https://ethereum.org/en/whitepaper/

Toast, Infernal and Logelin, Jay, 2018. *"0xBitcoin: The Decentralized Bitcoin Token for Ethereum"*.
<br>
	https://github.com/0xbitcoin/white-paper

Vogelsteller, Fabian and Buterin, Vitalik, 2015. *"EIP-20: ERC-20 Token Standard"*
<br>
	https://ethereum.org/en/developers/docs/standards/tokens/erc-20/

Logelin, Jay; Toast, Infernal; Seiler, Michael and Grill, Brandon, 2018. *"EIP-918: Mineable Token Standard"*
<br>
	https://eips.ethereum.org/EIPS/eip-918