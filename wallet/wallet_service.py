"""
Web3 Wallet Service for Apollo

Manages user wallets and token rewards:
- Create/connect wallets
- Track FIL, TFUEL, WTF balances
- Auto-convert to WTF
- Claim rewards
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import asyncio
import os

from web3 import Web3
from eth_account import Account
import httpx

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Supported tokens"""
    FIL = "FIL"          # Filecoin
    TFUEL = "TFUEL"      # Theta Fuel
    WTF = "WTF"          # Platform token
    ETH = "ETH"          # Ethereum (for gas)


class WalletService:
    """
    Manages Web3 wallets and token rewards
    
    Features:
    - Create new wallets
    - Connect existing wallets
    - Track token balances
    - Auto-convert to WTF
    - Claim rewards
    """
    
    def __init__(
        self,
        ethereum_rpc: str = None,
        filecoin_api: str = None,
        theta_api: str = None,
        delt_exchange_api: str = None
    ):
        # Web3 connections
        self.web3 = Web3(Web3.HTTPProvider(
            ethereum_rpc or os.getenv("ETHEREUM_RPC", "https://eth.llamarpc.com")
        ))
        
        # API clients
        self.filecoin_api = filecoin_api or os.getenv("FILECOIN_API")
        self.theta_api = theta_api or os.getenv("THETA_API")
        self.delt_api = delt_exchange_api or os.getenv("DELT_API")
        
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        logger.info("🪙 Wallet Service initialized")
    
    # ========================================================================
    # Wallet Creation & Connection
    # ========================================================================
    
    async def create_wallet(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        Create new Web3 wallet for user
        
        Args:
            user_id: User ID
            password: Password to encrypt private key
        
        Returns:
            Wallet details with mnemonic (show once!)
        """
        
        logger.info(f"🔐 Creating wallet for user {user_id}")
        
        # Generate new account
        Account.enable_unaudited_hdwallet_features()
        account, mnemonic = Account.create_with_mnemonic()
        
        # Encrypt private key with user's password
        encrypted_key = self._encrypt_private_key(
            account.key.hex(),
            password
        )
        
        # Store in database
        wallet_data = {
            "user_id": user_id,
            "wallet_address": account.address,
            "encrypted_key": encrypted_key,
            "created_at": datetime.utcnow().isoformat(),
            "auto_convert_fil": True,   # Default: auto-convert
            "auto_convert_tfuel": True
        }
        
        # TODO: Store in database
        # await self.db.wallets.insert_one(wallet_data)
        
        logger.info(f"✅ Wallet created: {account.address}")
        
        return {
            "address": account.address,
            "mnemonic": mnemonic,  # SHOW ONCE! User must save
            "auto_convert_enabled": True
        }
    
    async def connect_wallet(
        self,
        user_id: str,
        wallet_address: str,
        signature: str,
        message: str = None
    ) -> bool:
        """
        Connect existing wallet via signature verification
        
        Args:
            user_id: User ID
            wallet_address: Wallet address to connect
            signature: Signature from wallet
            message: Message that was signed
        
        Returns:
            True if verified and connected
        """
        
        logger.info(f"🔗 Connecting wallet {wallet_address} for user {user_id}")
        
        # Default message if not provided
        if not message:
            message = f"Connect wallet to Atlas\nUser ID: {user_id}\nTimestamp: {datetime.utcnow().isoformat()}"
        
        # Verify signature
        try:
            recovered_address = Account.recover_message(
                message,
                signature=signature
            )
            
            if recovered_address.lower() != wallet_address.lower():
                raise ValueError("Signature verification failed")
        
        except Exception as e:
            logger.error(f"❌ Signature verification failed: {e}")
            return False
        
        # Store wallet connection
        wallet_data = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "connected_at": datetime.utcnow().isoformat(),
            "connection_type": "external",
            "auto_convert_fil": True,
            "auto_convert_tfuel": True
        }
        
        # TODO: Store in database
        # await self.db.wallets.insert_one(wallet_data)
        
        logger.info(f"✅ Wallet connected: {wallet_address}")
        
        return True
    
    # ========================================================================
    # Token Rewards
    # ========================================================================
    
    async def credit_storage_reward(
        self,
        user_id: str,
        cid: str,
        size_mb: float
    ) -> Dict[str, Any]:
        """
        Credit FIL for data storage
        
        Args:
            user_id: User ID
            cid: Filecoin CID
            size_mb: Size in MB
        
        Returns:
            Reward details
        """
        
        # Calculate reward
        # Filecoin pays ~$0.005 per GB per month
        # Daily rate: $0.005 / 30 = $0.000167 per GB per day
        reward_usd_per_day = (size_mb / 1000) * 0.000167
        
        # Convert to FIL (assume $24 per FIL)
        fil_price = await self._get_fil_price()
        reward_fil = reward_usd_per_day / fil_price
        
        # Get user's wallet
        wallet = await self._get_user_wallet(user_id)
        
        # Credit FIL
        reward = {
            "token": "FIL",
            "amount": reward_fil,
            "amount_usd": reward_usd_per_day,
            "reason": "storage_reward",
            "metadata": {
                "cid": cid,
                "size_mb": size_mb
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._credit_token(wallet["wallet_address"], reward)
        
        # Auto-convert if enabled
        if wallet.get("auto_convert_fil"):
            await self._auto_convert_to_wtf(user_id, "FIL", reward_fil)
        
        logger.info(f"💾 Storage reward: {reward_fil} FIL for {size_mb}MB")
        
        return reward
    
    async def credit_compute_reward(
        self,
        user_id: str,
        job_id: str,
        gpu_hours: float
    ) -> Dict[str, Any]:
        """
        Credit TFUEL for GPU compute
        
        Args:
            user_id: User ID
            job_id: Training job ID
            gpu_hours: GPU hours used
        
        Returns:
            Reward details
        """
        
        # Calculate reward
        # Theta pays ~0.25 TFUEL per GPU hour
        reward_tfuel = gpu_hours * 0.25
        
        # Convert to USD (assume $0.25 per TFUEL)
        tfuel_price = await self._get_tfuel_price()
        reward_usd = reward_tfuel * tfuel_price
        
        # Get user's wallet
        wallet = await self._get_user_wallet(user_id)
        
        # Credit TFUEL
        reward = {
            "token": "TFUEL",
            "amount": reward_tfuel,
            "amount_usd": reward_usd,
            "reason": "compute_reward",
            "metadata": {
                "job_id": job_id,
                "gpu_hours": gpu_hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._credit_token(wallet["wallet_address"], reward)
        
        # Auto-convert if enabled
        if wallet.get("auto_convert_tfuel"):
            await self._auto_convert_to_wtf(user_id, "TFUEL", reward_tfuel)
        
        logger.info(f"⚡ Compute reward: {reward_tfuel} TFUEL for {gpu_hours}h")
        
        return reward
    
    # ========================================================================
    # Auto-Convert to WTF
    # ========================================================================
    
    async def _auto_convert_to_wtf(
        self,
        user_id: str,
        from_token: str,
        amount: float
    ) -> float:
        """
        Auto-convert tokens to WTF on Delt exchange
        
        Args:
            user_id: User ID
            from_token: Source token (FIL or TFUEL)
            amount: Amount to convert
        
        Returns:
            WTF amount received
        """
        
        logger.info(f"🔄 Auto-converting {amount} {from_token} to WTF")
        
        # Get user's wallet
        wallet = await self._get_user_wallet(user_id)
        
        # Swap on Delt exchange
        try:
            response = await self.http_client.post(
                f"{self.delt_api}/swap",
                json={
                    "from_token": from_token,
                    "to_token": "WTF",
                    "amount": amount,
                    "wallet_address": wallet["wallet_address"]
                }
            )
            
            swap_result = response.json()
            wtf_amount = swap_result["wtf_received"]
            
            # Credit WTF
            wtf_reward = {
                "token": "WTF",
                "amount": wtf_amount,
                "reason": "auto_convert",
                "metadata": {
                    "from_token": from_token,
                    "from_amount": amount
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self._credit_token(wallet["wallet_address"], wtf_reward)
            
            logger.info(f"✅ Converted to {wtf_amount} WTF")
            
            return wtf_amount
            
        except Exception as e:
            logger.error(f"❌ Auto-convert failed: {e}")
            return 0.0
    
    # ========================================================================
    # Balance Queries
    # ========================================================================
    
    async def get_balances(self, user_id: str) -> Dict[str, Dict]:
        """
        Get all token balances for user
        
        Returns:
            Dict of token balances with USD values
        """
        
        wallet = await self._get_user_wallet(user_id)
        address = wallet["wallet_address"]
        
        # Get balances
        fil_balance = await self._get_fil_balance(address)
        tfuel_balance = await self._get_tfuel_balance(address)
        wtf_balance = await self._get_wtf_balance(address)
        
        # Get prices
        fil_price = await self._get_fil_price()
        tfuel_price = await self._get_tfuel_price()
        wtf_price = await self._get_wtf_price()
        
        return {
            "FIL": {
                "balance": fil_balance,
                "price_usd": fil_price,
                "value_usd": fil_balance * fil_price
            },
            "TFUEL": {
                "balance": tfuel_balance,
                "price_usd": tfuel_price,
                "value_usd": tfuel_balance * tfuel_price
            },
            "WTF": {
                "balance": wtf_balance,
                "price_usd": wtf_price,
                "value_usd": wtf_balance * wtf_price
            },
            "total_usd": (
                fil_balance * fil_price +
                tfuel_balance * tfuel_price +
                wtf_balance * wtf_price
            )
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _encrypt_private_key(self, private_key: str, password: str) -> str:
        """Encrypt private key with password"""
        # TODO: Implement proper encryption (AES-256)
        # For now, placeholder
        return f"encrypted_{private_key}"
    
    async def _get_user_wallet(self, user_id: str) -> Dict:
        """Get user's wallet from database"""
        # TODO: Implement database query
        # For now, placeholder
        return {
            "user_id": user_id,
            "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "auto_convert_fil": True,
            "auto_convert_tfuel": True
        }
    
    async def _credit_token(self, wallet_address: str, reward: Dict):
        """Credit token to wallet"""
        # TODO: Implement actual token transfer
        # For now, just log
        logger.info(f"💰 Credited {reward['amount']} {reward['token']} to {wallet_address}")
    
    async def _get_fil_balance(self, address: str) -> float:
        """Get FIL balance"""
        # TODO: Query Filecoin network
        return 0.0234
    
    async def _get_tfuel_balance(self, address: str) -> float:
        """Get TFUEL balance"""
        # TODO: Query Theta network
        return 12.45
    
    async def _get_wtf_balance(self, address: str) -> float:
        """Get WTF balance"""
        # TODO: Query Delt exchange
        return 150.0
    
    async def _get_fil_price(self) -> float:
        """Get FIL price in USD"""
        # TODO: Query price oracle
        return 24.0
    
    async def _get_tfuel_price(self) -> float:
        """Get TFUEL price in USD"""
        # TODO: Query price oracle
        return 0.25
    
    async def _get_wtf_price(self) -> float:
        """Get WTF price in USD"""
        # TODO: Query Delt exchange
        return 0.10
