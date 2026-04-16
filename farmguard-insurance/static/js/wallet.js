let walletAddress = null;

function isPhantomInstalled() {
    return window.solana && window.solana.isPhantom;
}

async function connectWallet() {
    if (!isPhantomInstalled()) {
        alert('Please install Phantom Wallet to use FarmGuard!');
        window.open('https://phantom.app/', '_blank');
        return;
    }

    try {
        const resp = await window.solana.connect();
        walletAddress = resp.publicKey.toString();
        
        const btn = document.getElementById('walletBtn');
        btn.innerText = walletAddress.substring(0, 4) + '...' + walletAddress.substring(walletAddress.length - 4);
        btn.style.background = '#059669';
        
        console.log("Connected to wallet:", walletAddress);
    } catch (err) {
        console.error("Connection failed", err);
    }
    
}

async function updateWalletUI(address) {
    // You can call your Flask API which uses the Helius RPC
    const response = await fetch(`/api/blockchain/balance?address=${address}`);
    const data = await response.json();
    
    document.getElementById('wallet-balance').innerText = `${data.balance.toFixed(4)} SOL`;
}