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


    //event TokenApproval(address indexed tokenOwner, address indexed spender, uint tokens);
    //event TokenTransfer(address indexed from, address indexed to, uint tokens);


    mapping(address => uint256) balances;

    mapping(address => mapping (address => uint256)) allowed;

    uint256 totalSupply_ = 10 ether;

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
        balances[msg.sender] = balances[msg.sender].sub(numTokens);
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
        require(numTokens <= balances[owner]);
        require(numTokens <= allowed[owner][msg.sender]);

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

    struct Pool {
        uint256 eth_pool;
        uint256 token_pool;
    }

    event Bought(uint256 amount);
    event Sold(uint256 amount);

    // TODO: 
    //CREATE POOL FOR EACH TOKEN: POOL = {eth_pool: uint256, token_pool: uint256 , token: address(ERC20) } 
    // IMPLEMENT ethToTokenSwap, tokenToEthSwap, check about token2token
    // IMPLEMENT Invest in pool
    IERC20 public token;
    mapping(IERC20 => Pool) pools;

    // token price for ETH
    uint256 public tokensPerEth = 100;

    // Event that log buy operation
    event BuyTokens(address buyer, uint256 amountOfETH, uint256 amountOfTokens);
    event SellTokens(address seller, uint256 amountOfTokens, uint256 amountOfETH);

    constructor() public {
        token = new ERC20Basic();
        pools[token] = Pool(0,0);
    }

    function getPool(IERC20 _token) public view returns (uint256, uint256) {
        return (pools[_token].eth_pool, pools[_token].token_pool);
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


    function buy() payable public {
        uint256 amountTobuy = msg.value;
        uint256 dexBalance = token.balanceOf(address(this));
        require(amountTobuy > 0, "You need to send some ether");
        require(amountTobuy <= dexBalance, "Not enough tokens in the reserve");
        token.transfer(msg.sender, amountTobuy);
        emit Bought(amountTobuy);
    }

    function sell(uint256 amount) public {
        require(amount > 0, "You need to sell at least some tokens");
        uint256 allowance = token.allowance(msg.sender, address(this));
        require(allowance >= amount, "Check the token allowance");
        token.transferFrom(msg.sender, address(this), amount);
        payable(msg.sender).transfer(amount);
        emit Sold(amount);
    }

    // function ethToTokenSwap(uint256 eth_amount){
    //     require(eth_amount > 0, "You need to sell at least some ether");
    // }

    // def ethToTokenSwap():
    // fee: uint256 = msg.value / 500 
    // invariant: uint256 = self.eth_pool * self.token_pool
    // new_eth_pool: uint256 = self.eth_pool + msg.value
    // new_token_pool: uint256 = invariant / (new_eth_pool - fee)
    // tokens_out: uint256 = self.token_pool - new_token_pool
    // self.eth_pool = new_eth_pool
    // self.token_pool = new_token_pool
    // self.token.transfer(msg.sender, tokens_out)


    // @public
    // def tokenToEthSwap(tokens_in: uint256):
    //     fee: uint256 = tokens_in / 500
    //     invariant: uint256 = self.eth_pool * self.token_pool
    //     new_token_pool: uint256 = self.token_pool + tokens_in
    //     new_eth_pool: uint256 = self.invariant / (new_token_pool - fee)
    //     eth_out: uint256 = self.eth_pool - new_eth_pool
    //     self.eth_pool = new_eth_pool
    //     self.token_pool = new_token_pool
    //     self.token.transferFrom(msg.sender, self, tokens_out)
    //     send(msg.sender, eth_out)



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