"""
Plaid Parser Agent - LLM-Powered Bank Transaction Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw Plaid API
responses into structured financial transaction data.
"""

from typing import Dict, Any, List
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class PlaidParserAgent(Layer1Agent):
    """
    Plaid Parser - LLM-powered bank transaction parsing
    
    Takes raw Plaid API responses and extracts:
    - Transaction details (merchant, amount, category)
    - Spending patterns
    - Income sources
    - Recurring transactions
    - Anomaly detection
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="plaid_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered bank transaction and financial data parsing",
            capabilities=["transaction_parsing", "spending_analysis", "income_detection", "anomaly_detection"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured financial data from raw Plaid API response
        
        Args:
            raw_data: Raw Plaid API response (transactions, accounts, etc.)
            
        Returns:
            AgentResult with structured financial data
        """
        
        data_type = raw_data.get('type', 'transactions')
        
        if data_type == 'transactions':
            return await self._parse_transactions(raw_data)
        elif data_type == 'accounts':
            return await self._parse_accounts(raw_data)
        elif data_type == 'identity':
            return await self._parse_identity(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_transactions(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse transactions with LLM"""
        
        transactions = raw_data.get('transactions', [])
        
        prompt = f"""You are an expert financial data parser. Analyze these bank transactions and extract insights.

RAW TRANSACTIONS:
{json.dumps(transactions[:10], indent=2)}  # Limit to 10 for context

For EACH transaction, extract:
1. Merchant name (cleaned and standardized)
2. Amount and currency
3. Date
4. Category (groceries, dining, transportation, utilities, etc.)
5. Is this a recurring transaction? (yes/no)
6. Is this income or expense?
7. Any anomalies? (unusual amount, new merchant, etc.)

Also provide:
8. Spending patterns (top categories, trends)
9. Recurring transactions identified
10. Income sources identified
11. Any suspicious activity

Return as JSON:
{{
    "transactions": [
        {{
            "merchant": "...",
            "amount": 0,
            "currency": "USD",
            "date": "...",
            "category": "...",
            "is_recurring": false,
            "type": "expense|income",
            "anomaly": null
        }}
    ],
    "insights": {{
        "spending_patterns": {{}},
        "recurring_transactions": [],
        "income_sources": [],
        "suspicious_activity": []
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_transactions_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={
                    'agent': self.metadata.name,
                    'type': 'transactions',
                    'model': 'phi-3-medium',
                    'transaction_count': len(transactions)
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_accounts(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse account information with LLM"""
        
        accounts = raw_data.get('accounts', [])
        
        prompt = f"""Extract and analyze bank account information.

RAW ACCOUNTS:
{json.dumps(accounts, indent=2)}

For each account, extract:
1. Account name and type (checking, savings, credit, etc.)
2. Current balance
3. Available balance
4. Institution name
5. Account health (good, warning, critical based on balance)

Return as JSON.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_accounts_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'accounts'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_identity(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse identity information with LLM"""
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic parsing for unknown Plaid data types"""
        pass
    
    async def _store_transactions_in_kg(self, transaction_data: Dict[str, Any]):
        """Store parsed transactions in knowledge graph"""
        if not self.kg_client:
            return
        
        for txn in transaction_data.get('transactions', []):
            # Create transaction entity
            await self.kg_client.create_entity(
                entity_type="transaction",
                data=txn
            )
            
            # Create merchant entity if new
            await self.kg_client.create_entity(
                entity_type="merchant",
                data={'name': txn['merchant'], 'category': txn['category']}
            )
            
            # Create relationship
            await self.kg_client.create_relationship(
                from_entity="user",
                to_entity="transaction",
                relationship_type="made_transaction"
            )
    
    async def _store_accounts_in_kg(self, account_data: Dict[str, Any]):
        """Store parsed accounts in knowledge graph"""
        if not self.kg_client:
            return
        
        for account in account_data.get('accounts', []):
            await self.kg_client.create_entity(
                entity_type="bank_account",
                data=account
            )
