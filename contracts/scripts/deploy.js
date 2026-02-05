const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  // 1. Deploy CUSDT
  const CUSDT = await hre.ethers.getContractFactory("CUSDT");
  const cusdt = await CUSDT.deploy();
  await cusdt.waitForDeployment();
  const cusdtAddress = await cusdt.getAddress();
  console.log("CUSDT deployed to:", cusdtAddress);

  // 2. Deploy CommitmentEscrow (wired to CUSDT)
  const CommitmentEscrow = await hre.ethers.getContractFactory("CommitmentEscrow");
  const escrow = await CommitmentEscrow.deploy(cusdtAddress);
  await escrow.waitForDeployment();
  const escrowAddress = await escrow.getAddress();
  console.log("CommitmentEscrow deployed to:", escrowAddress);

  console.log("Chain ID: 11155111 (Sepolia)");

  // 3. Write Artifacts to Frontend
  const outDir = path.join(__dirname, "..", "..", "frontend", "lib", "contracts");
  fs.mkdirSync(outDir, { recursive: true });

  const writeArtifact = async (name, address, contractArtifact) => {
    fs.writeFileSync(
      path.join(outDir, `${name}.json`),
      JSON.stringify(
        { address, abi: contractArtifact.abi, chainId: 11155111 },
        null,
        2
      ),
      "utf8"
    );
  };

  await writeArtifact("CUSDT", cusdtAddress, await hre.artifacts.readArtifact("CUSDT"));
  await writeArtifact("CommitmentEscrow", escrowAddress, await hre.artifacts.readArtifact("CommitmentEscrow"));

  console.log("ABIs + addresses written to frontend/lib/contracts/");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
