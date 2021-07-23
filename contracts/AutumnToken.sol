//SPDX-License-Identifier: MIT
pragma solidity 0.8.5;


import "../interfaces/ERC20.sol";
import "../interfaces/ERC918.sol";
import "../interfaces/Owned.sol";
import "../interfaces/ApproveAndCallFallBack.sol";


// ----------------------------------------------------------------------------

// 'Autumn Token' contract

// ERC20 & ERC918 Mineable Token using Proof Of Work

// Symbol      : AUTUMN

// Name        : Autumn Token

// Total supply: 33,112,800.00

// Decimals    : 18

// Initial mining reward: 120

// Fraction of total supply released before first halving: 3/7

// ----------------------------------------------------------------------------





contract AutumnToken is ERC20Interface, ERC918, Owned {

    string public constant symbol = "AUTUMN";

    string public constant name = "Autumn Token";

    uint public constant TOKEN_IDENTIFIER = 3;

    uint8 public constant DECIMALS = 18;

    uint public constant TOTAL_SUPPLY = 33112800 * 10**18;

    uint public constant INITIAL_REWARD = 120 * 10**18;

    uint public constant MAX_REWARDS_AVAILABLE = 72; // no more than 72 rewards per mint

    uint public constant REWARD_INTERVAL = 600; // rewards every ten minutes on average

    uint public constant DURATION_OF_FIRST_ERA = (365 * 24 * 60 * 60 * 9) / 4; // 27 months

    uint public constant DURATION_OF_ERA = 3 * 365 * 24 * 60 * 60; // three years

    uint public constant MINIMUM_TARGET = 2**16;

    uint public constant MAXIMUM_TARGET = 2**234;

    uint public immutable contractCreationTime;

    uint public lastRewardBlockTime;

    uint public maxNumberOfRewardsPerMint;

    bytes32 public challengeNumber;
        
    uint public miningTarget;

    uint public tokensMinted;

    bool internal locked = false;

    mapping(address => uint) internal balances;

    mapping(address => mapping(address => uint)) internal allowed;


    constructor() onlyOwner {
        
        if (locked) revert();
        locked = true;

        miningTarget = MAXIMUM_TARGET / 2**10;

        contractCreationTime = block.timestamp;
        lastRewardBlockTime = block.timestamp;

        maxNumberOfRewardsPerMint = 1;

        challengeNumber = _getNewChallengeNumber(0);

    }


    function mint(uint256 nonce) override public returns (bool success) {

        uint _lastRewardBlockTime = lastRewardBlockTime;
        
        uint singleRewardAmount = _getMiningReward(_lastRewardBlockTime);

        // no more minting when reward reaches zero
        if (singleRewardAmount == 0) revert("Reward has reached zero");

        // the PoW must contain work that includes the challenge number and the msg.sender's address
        bytes32 digest =  keccak256(abi.encodePacked(challengeNumber, msg.sender, nonce));

        uint _miningTarget = miningTarget;
        // the digest must be smaller than the target
        if (uint256(digest) > _miningTarget) revert();

        uint _previousMaxNumberOfRewards = maxNumberOfRewardsPerMint;
        uint numberOfRewardsToGive = _numberOfRewardsToGive(_miningTarget / uint256(digest), 
                                                            _lastRewardBlockTime,
                                                            _previousMaxNumberOfRewards,
                                                            block.timestamp);
        uint totalRewardAmount = singleRewardAmount * numberOfRewardsToGive;

        uint _tokensMinted = _giveRewards(totalRewardAmount);
        
        _setNextMaxNumberOfRewards(numberOfRewardsToGive, _previousMaxNumberOfRewards);

        miningTarget = _adjustDifficulty(_miningTarget, _lastRewardBlockTime,
                                         numberOfRewardsToGive, block.timestamp);

        bytes32 newChallengeNumber = _getNewChallengeNumber(_tokensMinted);
        challengeNumber = newChallengeNumber;

        lastRewardBlockTime = block.timestamp;

        emit Mint(msg.sender, totalRewardAmount, _scheduledNumberOfRewards(block.timestamp), 
                  newChallengeNumber);

        return true;
    }

    function _numberOfRewardsAvailable(uint _lastRewardBlockTime, 
                                       uint _previousMaxNumberOfRewards, 
                                       uint currentTime) internal pure returns (uint) {

        uint numberAvailable = _previousMaxNumberOfRewards;
        uint intervalsSinceLastReward = (currentTime - _lastRewardBlockTime) / REWARD_INTERVAL;
        
        if (intervalsSinceLastReward > numberAvailable)
            numberAvailable = intervalsSinceLastReward;

        if (numberAvailable > MAX_REWARDS_AVAILABLE)
            numberAvailable = MAX_REWARDS_AVAILABLE;

        return numberAvailable;
    }

    function _numberOfRewardsToGive(uint numberEarned, uint _lastRewardBlockTime, 
                                    uint _previousMaxNumberOfRewards,
                                    uint currentTime) internal pure returns (uint) {

        uint numberAvailable = _numberOfRewardsAvailable(_lastRewardBlockTime,
                                                         _previousMaxNumberOfRewards,
                                                         currentTime);
        if (numberEarned < numberAvailable)
            return numberEarned;

        return numberAvailable;
    }

    function _giveRewards(uint totalReward) internal returns (uint) {

        balances[msg.sender] += totalReward;
        uint _tokensMinted = tokensMinted + totalReward;
        tokensMinted = _tokensMinted;
        return _tokensMinted;
    }

    function _setNextMaxNumberOfRewards(uint numberOfRewardsGivenNow, 
                                       uint _previousMaxNumberOfRewards) internal {

        // the value of the rewards given to this miner presumably exceed the gas costs
        // for processing the transaction. the next miner can submit a proof of enough work
        // to claim up to the same number of rewards immediately, or, if gas costs have increased,
        // wait until the maximum number of rewards claimable has increased enough to overcome
        // the costs.

        if (numberOfRewardsGivenNow != _previousMaxNumberOfRewards)
            maxNumberOfRewardsPerMint = numberOfRewardsGivenNow;
    }

    // backwards compatible mint function
    function mint(uint256 _nonce, bytes32 _challenge_digest) public returns (bool) {

        bytes32 digest = keccak256(abi.encodePacked(challengeNumber, msg.sender, _nonce));
        require(digest == _challenge_digest, "Challenge digest does not match expected digest on token contract [ AbstractERC918.mint() ]");
        
        return mint(_nonce);
    }

    function _getNewChallengeNumber(uint _tokensMinted) internal view returns (bytes32) {
        
        // make the latest ethereum block hash a part of the next challenge

        // xor with a number unique to this token to avoid merged mining
        
        // xor with the number of tokens minted to ensure that the challenge changes
        // even if there are multiple mints in the same ethereum block
        
        return bytes32(uint256(blockhash(block.number - 1)) ^ _tokensMinted ^ TOKEN_IDENTIFIER);
    }


    function _scheduledNumberOfRewards(uint currentTime) internal view returns (uint) {
        return (currentTime - contractCreationTime) / REWARD_INTERVAL;
    }

    function _adjustDifficulty(uint _miningTarget, 
                               uint _lastRewardBlockTime, 
                               uint rewardsGivenNow,
                               uint currentTime) internal pure returns (uint){

        uint timeSinceLastReward = currentTime - _lastRewardBlockTime;

        // we target a median interval of 10 minutes multiplied by log(2) ~ 61/88 
        // this gives a mean interval of 10 minutes per reward

        if (timeSinceLastReward * 88 < rewardsGivenNow * REWARD_INTERVAL * 61)
            _miningTarget = (_miningTarget / 100) * 99;   // slow down
        else
            _miningTarget = (_miningTarget / 99) * 100;   // speed up

        if (_miningTarget < MINIMUM_TARGET)
            _miningTarget = MINIMUM_TARGET;
        
        if (_miningTarget > MAXIMUM_TARGET) 
            _miningTarget = MAXIMUM_TARGET;

        return _miningTarget;
    }


    function rewardEra(uint _time) public view returns (uint) {

        uint timeSinceContractCreation = _time - contractCreationTime;

        if (timeSinceContractCreation < DURATION_OF_FIRST_ERA)
            return 0;
        else
            return 1 + (timeSinceContractCreation - DURATION_OF_FIRST_ERA) / DURATION_OF_ERA;
    }

    function getAdjustmentInterval() public view override returns (uint) {
        return REWARD_INTERVAL * maxNumberOfRewardsPerMint;
    }

    function getChallengeNumber() public view override returns (bytes32) {
        return challengeNumber;
    }

    function getMiningDifficulty() public view override returns (uint) {
        return 2 * (2**255 / miningTarget);
    }

    function getMiningTarget() public view override returns (uint) {
       return miningTarget;
   }

    function getMiningReward() public view override returns (uint) {

        // use the timestamp of the ethereum block that gave the last reward
        // because ethereum miners can manipulate the value of block.timestamp
        return _getMiningReward(lastRewardBlockTime);
    }

    function _getMiningReward(uint _time) internal view returns (uint) {
        return INITIAL_REWARD / 2**rewardEra(_time);
    }

    function getNumberOfRewardsAvailable(uint currentTime) public view returns (uint) {
        return _numberOfRewardsAvailable(lastRewardBlockTime, 
                                         maxNumberOfRewardsPerMint, 
                                         currentTime);
    }

    function getRewardAmountForAchievingTarget(uint targetAchieved, uint currentTime) public view returns (uint) {
        uint numberOfRewardsToGive = _numberOfRewardsToGive(miningTarget / targetAchieved, 
                                                            lastRewardBlockTime, 
                                                            maxNumberOfRewardsPerMint, 
                                                            currentTime);
        return _getMiningReward(currentTime) * numberOfRewardsToGive;
    }

    function decimals() public pure override returns (uint8) {
        return DECIMALS;
    }

    function totalSupply() public pure override returns (uint) {

        // this is an estimate of the final total supply. the actual number of tokens
        // minted in any era will depend on how the hashrate changes and may differ
        // slightly from the scheduled quantity

        return TOTAL_SUPPLY;
    }


    // ------------------------------------------------------------------------

    // Get the token balance for account `tokenOwner`

    // ------------------------------------------------------------------------

    function balanceOf(address tokenOwner) public view override returns (uint balance) {

        return balances[tokenOwner];

    }



    // ------------------------------------------------------------------------

    // Transfer the balance from token owner's account to `to` account

    // - Owner's account must have sufficient balance to transfer

    // - 0 value transfers are allowed

    // ------------------------------------------------------------------------

    function transfer(address to, uint tokens) public override returns (bool success) {
        
        require(to != address(0) && to != address(this));
        
        balances[msg.sender] = balances[msg.sender] - tokens;

        balances[to] = balances[to] + tokens;

        emit Transfer(msg.sender, to, tokens);

        return true;

    }



    // ------------------------------------------------------------------------

    // Token owner can approve for `spender` to transferFrom(...) `tokens`

    // from the token owner's account

    //

    // Warning: This function is vulnerable to double-spend attacks and is

    // included for backwards compatibility. Use safeApprove instead.

    // ------------------------------------------------------------------------

    function approve(address spender, uint tokens) public override returns (bool success) {

        allowed[msg.sender][spender] = tokens;

        emit Approval(msg.sender, spender, tokens);

        return true;

    }



    // ------------------------------------------------------------------------

    // Allow token owner to cancel the approval if the approved amount changes from its last

    // known value before this transaction is processed. This allows the owner to avoid 

    // unintentionally re-approving funds that have already been spent.

    // ------------------------------------------------------------------------

    function safeApprove(address spender, uint256 previousAllowance, uint256 newAllowance) public returns (bool success) {

        require(allowed[msg.sender][spender] == previousAllowance,
                "Current spender allowance does not match specified value");

        return approve(spender, newAllowance);
    }



    // ------------------------------------------------------------------------

    // Transfer `tokens` from the `from` account to the `to` account

    //

    // The calling account must already have sufficient tokens approve(...)-d

    // for spending from the `from` account and

    // - From account must have sufficient balance to transfer

    // - Spender must have sufficient allowance to transfer

    // - 0 value transfers are allowed

    // ------------------------------------------------------------------------

    function transferFrom(address from, address to, uint tokens) public override returns (bool success) {
        
        require(to != address(0) && to != address(this));

        balances[from] = balances[from] - tokens;

        allowed[from][msg.sender] = allowed[from][msg.sender] - tokens;

        balances[to] = balances[to] + tokens;

        emit Transfer(from, to, tokens);

        return true;

    }



    // ------------------------------------------------------------------------

    // Returns the amount of tokens approved by the owner that can be

    // transferred to the spender's account

    // ------------------------------------------------------------------------

    function allowance(address tokenOwner, address spender) public view override returns (uint remaining){

        return allowed[tokenOwner][spender];

    }



    // ------------------------------------------------------------------------

    // Token owner can approve for `spender` to transferFrom(...) `tokens`

    // from the token owner's account. The `spender` contract function

    // `receiveApproval(...)` is then executed

    //

    // Warning: This function is vulnerable to double-spend attacks and is

    // included for backwards compatibility. Use safeApproveAndCall instead.

    // ------------------------------------------------------------------------

    function approveAndCall(address spender, uint tokens, bytes memory data) public returns (bool success) {

        allowed[msg.sender][spender] = tokens;

        emit Approval(msg.sender, spender, tokens);

        ApproveAndCallFallBack(spender).receiveApproval(msg.sender, tokens, address(this), data);

        return true;

    }


    // ------------------------------------------------------------------------

    // Allow safe approvals with calls to receiving contract

    // ------------------------------------------------------------------------

    function safeApproveAndCall(address spender, uint256 previousAllowance, 
                                uint256 newAllowance, bytes memory data) public returns (bool success) {

        require(allowed[msg.sender][spender] == previousAllowance,
                "Current spender allowance does not match specified value");

        return approveAndCall(spender, newAllowance, data);
    }


    // ------------------------------------------------------------------------

    // Owner can transfer out any accidentally sent ERC20 tokens

    // ------------------------------------------------------------------------

    function transferAnyERC20Token(address tokenAddress, uint tokens) public onlyOwner returns (bool success) {

        return ERC20Interface(tokenAddress).transfer(owner, tokens);

    }

}
