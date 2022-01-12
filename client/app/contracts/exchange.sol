pragma solidity >=0.7.0 <0.9.0;
interface IERC20 {

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);

    function transfer(address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);


    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}


contract ERC20Basic is IERC20 {

    string public constant name = "ERC20Basic";
    string public constant symbol = "ERC";
    uint8 public constant decimals = 18;


    event TokenApproval(address indexed tokenOwner, address indexed spender, uint tokens);
    event TokenTransfer(address indexed from, address indexed to, uint tokens);


    mapping(address => uint256) balances;

    mapping(address => mapping (address => uint256)) allowed;

    uint256 totalSupply_ = 100 ether;

    using SafeMath for uint256;

   constructor() public {
    balances[msg.sender] = totalSupply_;

    }

    function totalSupply() public override view returns (uint256) {
    return totalSupply_;
    }

    function balanceOf(address tokenOwner) public override view returns (uint256) {
        return balances[tokenOwner];
    }

    function transfer(address receiver, uint256 numTokens) public override returns (bool) {
        require(numTokens <= balances[msg.sender]);
        //balances[msg.sender] = balances[msg.sender].sub(numTokens);
        balances[msg.sender] = balances[msg.sender] - numTokens;
        balances[receiver] = balances[receiver].add(numTokens);
        emit Transfer(msg.sender, receiver, numTokens);
        return true;
    }

    function approve(address delegate, uint256 numTokens) public override returns (bool) {
        allowed[msg.sender][delegate] = numTokens;
        emit Approval(msg.sender, delegate, numTokens);
        return true;
    }

    function allowance(address owner, address delegate) public override view returns (uint) {
        return allowed[owner][delegate];
    }

    function transferFrom(address owner, address buyer, uint256 numTokens) public override returns (bool) {
        require(numTokens < balances[owner], "not enough tokens in balance");
        require(numTokens < allowed[owner][msg.sender], "not allowed");

        balances[owner] = balances[owner].sub(numTokens);
        allowed[owner][msg.sender] = allowed[owner][msg.sender].sub(numTokens);
        balances[buyer] = balances[buyer].add(numTokens);
        emit Transfer(owner, buyer, numTokens);
        return true;
    }
}

library SafeMath {
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
      assert(b <= a);
      return a - b;
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
      uint256 c = a + b;
      assert(c >= a);
      return c;
    }
}



contract DEX {

    // struct Pool {
    //     uint256 eth_pool;
    //     uint256 token_pool;
    // }

    event Bought(uint256 amount);
    event Sold(uint256 amount);


    IERC20 public token;

    uint256 private balance_tok;
    uint256 private balance_eth;
    uint256 private balance_lqt;

    // token price for ETH
    uint256 public tokensPerEth = 100;

    uint256 public eth_tok_invariant;
    uint256 public eth_lqt_invariant;

    mapping(address => uint256) shares;   
    // Event that log buy operation
    event BuyTokens(address buyer, uint256 amountOfETH, uint256 amountOfTokens);
    event SellTokens(address seller, uint256 amountOfTokens, uint256 amountOfETH);
    

    constructor() public {
        token = new ERC20Basic();
        balance_tok = 0;
        balance_eth = 0;
        balance_lqt = 0;
        eth_tok_invariant = 0;
        eth_lqt_invariant = 0;
    }

    // function getPool(IERC20 _token) public view returns (uint256, uint256) {
    //     return (pools[_token].eth_pool, pools[_token].token_pool);
    // }


    function getContractBalance() public view returns (uint256, uint256) { //view amount of ETH and Tok the contract contains
        return (address(this).balance, token.balanceOf(address(this)));
    }


    function buyTokens(uint eth_amount) public payable returns (uint256 tokenAmount) {
        require(eth_amount > 0, "Send ETH to buy some tokens");

        uint256 amountToBuy = eth_amount * tokensPerEth;

        // check if the Vendor Contract has enough amount of tokens for the transaction
        uint256 vendorBalance = token.balanceOf(address(this));
        require(vendorBalance >= amountToBuy, "Vendor contract has not enough tokens in its balance");

        // Transfer token to the msg.sender
        (bool sent) = token.transfer(msg.sender, amountToBuy);
        require(sent, "Failed to transfer token to user");

        // emit the event
        emit BuyTokens(msg.sender, eth_amount, amountToBuy);

        return amountToBuy;
    }


    function sellTokens(uint256 tokenAmountToSell) public {//returns (bool) {
        // Check that the requested amount of tokens to sell is more than 0
        require(tokenAmountToSell > 0, "Specify an amount of token greater than zero");

        // Check that the user's token balance is enough to do the swap
        uint256 userBalance = token.balanceOf(msg.sender);
        require(userBalance > tokenAmountToSell, "Your balance is lower than the amount of tokens you want to sell");

        // Check that the Vendor's balance is enough to do the swap
        uint256 amountOfETHToTransfer = tokenAmountToSell / tokensPerEth;
        uint256 ownerETHBalance = address(this).balance;
        require(ownerETHBalance > amountOfETHToTransfer, "Vendor has not enough funds to accept the sell request");

        (bool sent) = token.transferFrom(msg.sender, address(this), tokenAmountToSell);
        require(sent, "Failed to transfer tokens from user to vendor");

        payable(msg.sender).transfer(amountOfETHToTransfer);
        //(sent,) = msg.sender.call{value: amountOfETHToTransfer}("");
        //require(sent, "Failed to send ETH to the user");
    }

    function approve(address delegate, uint256 numTokens) public returns (bool) {
        (bool approved) = token.approve(delegate, numTokens);
        return approved;
    }

    function getTokenContractAddress() public view returns (address token_address){
        return address(token);
    }

    function getTokBalance(address tokenOwner) public view returns (uint256){
        return token.balanceOf(tokenOwner);
    }

    // function buy() payable public {
    //     uint256 amountTobuy = msg.value;
    //     uint256 dexBalance = token.balanceOf(address(this));
    //     require(amountTobuy > 0, "You need to send some ether");
    //     require(amountTobuy <= dexBalance, "Not enough tokens in the reserve");
    //     token.transfer(msg.sender, amountTobuy);
    //     emit Bought(amountTobuy);
    // }

    // function sell(uint256 amount) public {
    //     require(amount > 0, "You need to sell at least some tokens");
    //     uint256 allowance = token.allowance(msg.sender, address(this));
    //     require(allowance >= amount, "Check the token allowance");
    //     token.transferFrom(msg.sender, address(this), amount);
    //     payable(msg.sender).transfer(amount);
    //     emit Sold(amount);
    // }



    // function ethToTokenSwap() public payable returns (uint256 tokenAmount){
    //     fee: uint256 = msg.value / 500 
    //     invariant: uint256 = self.eth_pool * self.token_pool
    //     new_eth_pool: uint256 = self.eth_pool + msg.value
    //     new_token_pool: uint256 = invariant / (new_eth_pool - fee)
    //     tokens_out: uint256 = self.token_pool - new_token_pool
    //     self.eth_pool = new_eth_pool
    //     self.token_pool = new_token_pool
    //     self.token.transfer(msg.sender, tokens_out)
    // }

    
    function tokenToEthSwap(uint256 tokens_in) public payable {
        require(tokens_in > 0, "You need to sell at least some tokens");
        uint256 allowance = token.allowance(msg.sender, address(this));
        require(allowance >= tokens_in, "Check the token allowance");
        uint256 fee = tokens_in / 500;
        uint256 invariant = balance_tok * balance_eth;
        uint256 new_token_pool = balance_tok + tokens_in;
        uint256 tokens_out = balance_tok - new_token_pool;
        uint256 new_eth_pool = invariant / (new_token_pool - fee);
        uint256 eth_out = balance_eth - new_eth_pool;
        balance_eth = new_eth_pool;
        balance_tok = new_token_pool;
        token.transferFrom(msg.sender, address(this), tokens_out);
        payable(msg.sender).transfer(eth_out);
    }


             
    //The first liquidity provider to invest in an exchange must initialise it. 
    //This is done by depositing some amount of both ETH and the exchange token into the contract, which sets the initial exchange rate. 
    //The provider is rewarded with initial “shares” of the market (based on the value deposited). 
    //These shares are Liquidity Tokens, which represent proportional ownership of a single Blockdrop exchange. 
    //Shares are highly divisible and can be burned at any time to return a proportional share of the markets liquidity to the owner.            
    function initialize(uint256 tokens_invested) public payable {
        require(balance_lqt == 0, "DEX: init - already has liquidity");
        require(tokens_invested > 0, "You must send some tokens to initialize");
        uint256 eth_invested = msg.value;
        require(eth_invested > 0, "You must send some ether to initialize");
        balance_eth = eth_invested;
        balance_tok = tokens_invested;
        eth_tok_invariant = balance_eth * balance_tok;
        uint256 initial_liquidity_tokens = (tokens_invested / eth_invested) / 2;
        balance_lqt = initial_liquidity_tokens;
        eth_lqt_invariant = balance_eth * balance_lqt;
        shares[msg.sender] = initial_liquidity_tokens;
        token.transferFrom(msg.sender, address(this), tokens_invested);
    }

    //     @public
    // def tokenToTokenSwap(token_addr: address, tokens_sold: uint256):
    //     exchange: address = Factory(self.factory_address).token_to_exchange_lookup(token_addr)
    //     fee: uint256 = tokens_sold / 500
    //     invariant: uint256 = self.eth_pool * self.token_pool
    //     new_token_pool: uint256 = self.token_pool + tokens_sold
    //     new_eth_pool: uint256 = invariant / (new_token_pool - fee)
    //     eth_out: uint256 = self.eth_pool - new_eth_pool
    //     self.eth_pool = new_eth_pool
    //     self.token_pool = new_token_pool
    //     Exchange(exchange).ethToTokenTransfer(msg.sender, value=eth_out)
}
