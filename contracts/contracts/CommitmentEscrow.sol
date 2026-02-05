// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title CommitmentEscrow
 * @notice Time-locks ERC20 tokens for savings discipline. No admin withdrawal, no yield, no penalties.
 * Funds unlock only after maturity; only the depositor may withdraw.
 */
contract CommitmentEscrow is ReentrancyGuard {
    IERC20 public immutable token;

    struct Commitment {
        address depositor;
        uint256 amount;
        uint256 unlockTimestamp;
        bytes32 commitmentId;
        bool withdrawn;
    }

    mapping(bytes32 => Commitment) public commitments;

    event CommitmentCreated(
        address indexed user,
        bytes32 indexed commitmentId,
        uint256 amount,
        uint256 unlockTimestamp
    );
    event CommitmentWithdrawn(
        address indexed user,
        bytes32 indexed commitmentId,
        uint256 amount
    );

    error CommitmentAlreadyExists(bytes32 commitmentId);
    error CommitmentNotFound(bytes32 commitmentId);
    error UnlockTimeNotReached(uint256 unlockTimestamp, uint256 currentTime);
    error NotDepositor(address caller, address depositor);
    error AlreadyWithdrawn(bytes32 commitmentId);

    constructor(address _token) {
        require(_token != address(0), "Token address cannot be 0");
        token = IERC20(_token);
    }

    /**
     * @notice Create an escrow commitment. Caller must approve token transfer first.
     * @param commitmentId Deterministic hash from backend.
     * @param unlockTimestamp Unix timestamp when funds become withdrawable.
     * @param amount Amount of tokens to lock.
     */
    function createCommitment(
        bytes32 commitmentId,
        uint256 unlockTimestamp,
        uint256 amount
    ) external {
        if (commitments[commitmentId].depositor != address(0)) {
            revert CommitmentAlreadyExists(commitmentId);
        }
        require(amount > 0, "Amount must be > 0");

        // Transfer tokens from user to this contract
        bool success = token.transferFrom(msg.sender, address(this), amount);
        require(success, "Transfer failed");

        commitments[commitmentId] = Commitment({
            depositor: msg.sender,
            amount: amount,
            unlockTimestamp: unlockTimestamp,
            commitmentId: commitmentId,
            withdrawn: false
        });

        emit CommitmentCreated(
            msg.sender,
            commitmentId,
            amount,
            unlockTimestamp
        );
    }

    /**
     * @notice Withdraw funds after unlock. Only the depositor may call.
     * @param commitmentId The commitment hash used at creation.
     */
    function withdraw(bytes32 commitmentId) external nonReentrant {
        Commitment storage c = commitments[commitmentId];
        if (c.depositor == address(0)) {
            revert CommitmentNotFound(commitmentId);
        }
        if (c.withdrawn) {
            revert AlreadyWithdrawn(commitmentId);
        }
        if (msg.sender != c.depositor) {
            revert NotDepositor(msg.sender, c.depositor);
        }
        if (block.timestamp < c.unlockTimestamp) {
            revert UnlockTimeNotReached(c.unlockTimestamp, block.timestamp);
        }

        c.withdrawn = true;
        uint256 amount = c.amount;

        bool success = token.transfer(msg.sender, amount);
        require(success, "Transfer failed");

        emit CommitmentWithdrawn(msg.sender, commitmentId, amount);
    }

    /**
     * @notice Get commitment details.
     * @param commitmentId The commitment hash.
     */
    function getCommitment(
        bytes32 commitmentId
    ) external view returns (Commitment memory) {
        return commitments[commitmentId];
    }
}
