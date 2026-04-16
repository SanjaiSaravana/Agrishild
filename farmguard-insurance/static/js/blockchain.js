/**
 * FarmGuard Blockchain Logic
 * Handles: Phantom Connection, Helius Balance, and Payout Simulation
 */

async function updateWalletStatus() {
    const balanceEl = document.getElementById('wallet-balance');
    const rpcStatusEl = document.getElementById('rpc-status');

    try {
        // 1. Check if Phantom is available
        let address = "6x66...devnet_address"; // Fallback address
        
        if (window.solana && window.solana.isPhantom) {
            try {
                // Connect to Phantom
                const resp = await window.solana.connect({ onlyIfTrusted: true });
                address = resp.publicKey.toString();
                console.log("Connected to Phantom:", address);
            } catch (err) {
                console.warn("Wallet not trusted yet, using manual login.");
            }
        }

        // 2. Fetch real-time balance from our backend
        const response = await fetch(`/api/blockchain/balance?address=${address}`);
        const data = await response.json();

        // 3. Update UI
        if (balanceEl) {
            balanceEl.innerText = `${data.balance.toFixed(4)} SOL`;
        }
        if (rpcStatusEl) {
            rpcStatusEl.innerText = "CONNECTED (HELIUS)";
        }

    } catch (error) {
        console.error("Blockchain sync failed:", error);
        if (balanceEl) balanceEl.innerText = "Error Syncing";
    }
}

// Function to simulate sending money to a real bank account
async function simulatePayout(type) {
    const btn = event.currentTarget;
    const originalText = btn.innerText;
    
    btn.innerText = "Processing SOL Payout...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/blockchain/check-trigger', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ trigger_type: type })
        });
        const result = await response.json();

        if (result.success) {
            // Add row to the transaction table
            addTransactionToTable(type, result.tx_hash);
            
            // SIMULATE BANK TRANSFER
            setTimeout(() => {
                alert(`⛓️ SOL Payout Confirmed!\n\nInitiating Bank Settlement...\n₹10,000 is being transferred to your linked bank account via Fiat Gateway.`);
                btn.innerText = "✅ Payout Completed";
                btn.style.background = "#059669";
            }, 1000);
        }
    } catch (e) {
        btn.innerText = originalText;
        btn.disabled = false;
        alert("Transaction failed. Check console.");
    }
}

function addTransactionToTable(type, hash) {
    const tableBody = document.getElementById('tx-ledger-body');
    const emptyRow = document.getElementById('empty-ledger-row');
    if (emptyRow) emptyRow.remove();

    const row = `
        <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 12px; font-size: 0.85rem;">${new Date().toLocaleDateString()}</td>
            <td style="padding: 12px; font-size: 0.85rem; font-weight: bold;">${type.toUpperCase()}</td>
            <td style="padding: 12px;"><span style="background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem;">SETTLED</span></td>
            <td style="padding: 12px; font-family: monospace; font-size: 0.8rem; color: #3b82f6;">${hash.substring(0,8)}...</td>
        </tr>
    `;
    tableBody.insertAdjacentHTML('afterbegin', row);
}

// Initialize on load and refresh every 30 seconds
document.addEventListener('DOMContentLoaded', updateWalletStatus);
setInterval(updateWalletStatus, 30000);