# Commitment Escrow Contracts

Solidity ^0.8.20, Hardhat, OpenZeppelin. Deploy to Ethereum Sepolia.

## Setup

```bash
cd contracts
npm install
cp .env.example .env
# Edit .env: SEPOLIA_RPC_URL, PRIVATE_KEY (deployer wallet)
```

## Build & Deploy

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

Deploy script writes `address` + `abi` + `chainId` to `frontend/lib/contracts/CommitmentEscrow.json`.

## Env

- `SEPOLIA_RPC_URL` – Sepolia RPC (e.g. https://rpc.sepolia.org or Alchemy/Infura).
- `PRIVATE_KEY` – Deployer private key (no `0x` prefix).
