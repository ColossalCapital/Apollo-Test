"""
QuestDB Client - Time-Series Data Storage

Stores:
- User activity (actions, events)
- API metrics (performance, latency)
- Agent performance (confidence, cost)
- Document events (uploads, parsing)
- Email metrics (sentiment, priority)
- Token earnings (FIL, TFUEL, WTF)

Fast ingestion: Millions of rows/sec
Optimized for time-series analytics
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from enum import Enum

logger = logging.getLogger(__name__)


class QuestDBClient:
    """
    Client for QuestDB time-series database
    
    Uses InfluxDB Line Protocol for fast ingestion
    """
    
    def __init__(
        self,
        host: str = "localhost",
        http_port: int = 9010,
        ilp_port: int = 9011
    ):
        self.host = host
        self.http_port = http_port
        self.ilp_port = ilp_port
        self.http_url = f"http://{host}:{http_port}"
        
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"📊 QuestDB client initialized: {self.http_url}")
    
    # ========================================================================
    # Schema Creation
    # ========================================================================
    
    async def create_schemas(self):
        """Create all required tables"""
        
        schemas = [
            # User activity
            """
            CREATE TABLE IF NOT EXISTS user_activity (
                timestamp TIMESTAMP,
                user_id SYMBOL,
                action SYMBOL,
                agent_type SYMBOL,
                duration_ms LONG,
                success BOOLEAN,
                metadata STRING
            ) timestamp(timestamp) PARTITION BY DAY;
            """,
            
            # API metrics
            """
            CREATE TABLE IF NOT EXISTS api_metrics (
                timestamp TIMESTAMP,
                endpoint SYMBOL,
                user_id SYMBOL,
                status_code INT,
                response_time_ms LONG,
                request_size LONG,
                response_size LONG
            ) timestamp(timestamp) PARTITION BY HOUR;
            """,
            
            # Agent performance
            """
            CREATE TABLE IF NOT EXISTS agent_performance (
                timestamp TIMESTAMP,
                agent_type SYMBOL,
                user_id SYMBOL,
                confidence DOUBLE,
                latency_ms LONG,
                tokens_used INT,
                cost_usd DOUBLE
            ) timestamp(timestamp) PARTITION BY DAY;
            """,
            
            # Document events
            """
            CREATE TABLE IF NOT EXISTS document_events (
                timestamp TIMESTAMP,
                user_id SYMBOL,
                document_id SYMBOL,
                event_type SYMBOL,
                file_size_mb DOUBLE,
                processing_time_ms LONG
            ) timestamp(timestamp) PARTITION BY DAY;
            """,
            
            # Email metrics
            """
            CREATE TABLE IF NOT EXISTS email_metrics (
                timestamp TIMESTAMP,
                user_id SYMBOL,
                email_id SYMBOL,
                action SYMBOL,
                sentiment SYMBOL,
                priority SYMBOL,
                has_action_items BOOLEAN
            ) timestamp(timestamp) PARTITION BY DAY;
            """,
            
            # Token earnings
            """
            CREATE TABLE IF NOT EXISTS token_earnings (
                timestamp TIMESTAMP,
                user_id SYMBOL,
                token_type SYMBOL,
                amount DOUBLE,
                reason SYMBOL,
                auto_converted BOOLEAN
            ) timestamp(timestamp) PARTITION BY HOUR;
            """
        ]
        
        for schema in schemas:
            try:
                await self._execute_sql(schema)
                logger.info("✅ Schema created")
            except Exception as e:
                logger.warning(f"Schema may already exist: {e}")
    
    # ========================================================================
    # User Activity Logging
    # ========================================================================
    
    async def log_activity(
        self,
        user_id: str,
        action: str,
        agent_type: str = None,
        duration_ms: int = 0,
        success: bool = True,
        metadata: Dict = None
    ):
        """
        Log user activity
        
        Args:
            user_id: User ID
            action: Action performed (e.g., "upload_document", "query_agent")
            agent_type: Agent used (if applicable)
            duration_ms: Duration in milliseconds
            success: Whether action succeeded
            metadata: Additional metadata
        """
        
        import json
        
        line = f"user_activity,user_id={user_id},action={action}"
        
        if agent_type:
            line += f",agent_type={agent_type}"
        
        line += f" duration_ms={duration_ms}i,success={success}"
        
        if metadata:
            line += f',metadata="{json.dumps(metadata)}"'
        
        await self._write_line(line)
    
    # ========================================================================
    # API Metrics
    # ========================================================================
    
    async def log_api_request(
        self,
        endpoint: str,
        user_id: str,
        status_code: int,
        response_time_ms: int,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Log API request metrics"""
        
        line = (
            f"api_metrics,endpoint={endpoint},user_id={user_id} "
            f"status_code={status_code}i,response_time_ms={response_time_ms}i,"
            f"request_size={request_size}i,response_size={response_size}i"
        )
        
        await self._write_line(line)
    
    # ========================================================================
    # Agent Performance
    # ========================================================================
    
    async def log_agent_performance(
        self,
        agent_type: str,
        user_id: str,
        confidence: float,
        latency_ms: int,
        tokens_used: int = 0,
        cost_usd: float = 0.0
    ):
        """Log agent performance metrics"""
        
        line = (
            f"agent_performance,agent_type={agent_type},user_id={user_id} "
            f"confidence={confidence},latency_ms={latency_ms}i,"
            f"tokens_used={tokens_used}i,cost_usd={cost_usd}"
        )
        
        await self._write_line(line)
    
    # ========================================================================
    # Document Events
    # ========================================================================
    
    async def log_document_event(
        self,
        user_id: str,
        document_id: str,
        event_type: str,
        file_size_mb: float = 0.0,
        processing_time_ms: int = 0
    ):
        """
        Log document event
        
        event_type: uploaded, parsed, analyzed, deleted
        """
        
        line = (
            f"document_events,user_id={user_id},document_id={document_id},"
            f"event_type={event_type} "
            f"file_size_mb={file_size_mb},processing_time_ms={processing_time_ms}i"
        )
        
        await self._write_line(line)
    
    # ========================================================================
    # Email Metrics
    # ========================================================================
    
    async def log_email_event(
        self,
        user_id: str,
        email_id: str,
        action: str,
        sentiment: str = "neutral",
        priority: str = "medium",
        has_action_items: bool = False
    ):
        """
        Log email event
        
        action: received, sent, analyzed, archived
        """
        
        line = (
            f"email_metrics,user_id={user_id},email_id={email_id},"
            f"action={action},sentiment={sentiment},priority={priority} "
            f"has_action_items={has_action_items}"
        )
        
        await self._write_line(line)
    
    # ========================================================================
    # Token Earnings
    # ========================================================================
    
    async def log_token_earning(
        self,
        user_id: str,
        token_type: str,
        amount: float,
        reason: str,
        auto_converted: bool = False
    ):
        """
        Log token earnings
        
        token_type: FIL, TFUEL, WTF
        reason: storage, compute, referral, etc.
        """
        
        line = (
            f"token_earnings,user_id={user_id},token_type={token_type},"
            f"reason={reason} "
            f"amount={amount},auto_converted={auto_converted}"
        )
        
        await self._write_line(line)
    
    # ========================================================================
    # Query Methods
    # ========================================================================
    
    async def query(self, sql: str) -> List[Dict]:
        """Execute SQL query"""
        
        response = await self.http_client.get(
            f"{self.http_url}/exec",
            params={"query": sql}
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed: {response.text}")
        
        result = response.json()
        
        # Convert to list of dicts
        if "dataset" not in result:
            return []
        
        columns = result.get("columns", [])
        rows = result.get("dataset", [])
        
        return [
            {col["name"]: row[i] for i, col in enumerate(columns)}
            for row in rows
        ]
    
    async def get_user_activity(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict]:
        """Get user activity for last N days"""
        
        sql = f"""
        SELECT 
            timestamp,
            action,
            agent_type,
            duration_ms,
            success
        FROM user_activity
        WHERE user_id = '{user_id}'
          AND timestamp > dateadd('d', -{days}, now())
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        
        return await self.query(sql)
    
    async def get_token_earnings(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, float]:
        """Get user's token earnings"""
        
        sql = f"""
        SELECT 
            token_type,
            sum(amount) as total
        FROM token_earnings
        WHERE user_id = '{user_id}'
          AND timestamp > dateadd('d', -{days}, now())
        GROUP BY token_type
        """
        
        results = await self.query(sql)
        
        return {
            row["token_type"]: row["total"]
            for row in results
        }
    
    async def get_agent_performance_stats(
        self,
        agent_type: str = None,
        days: int = 7
    ) -> Dict:
        """Get agent performance statistics"""
        
        where_clause = ""
        if agent_type:
            where_clause = f"AND agent_type = '{agent_type}'"
        
        sql = f"""
        SELECT 
            agent_type,
            avg(confidence) as avg_confidence,
            avg(latency_ms) as avg_latency,
            sum(cost_usd) as total_cost,
            count() as request_count
        FROM agent_performance
        WHERE timestamp > dateadd('d', -{days}, now())
          {where_clause}
        GROUP BY agent_type
        ORDER BY request_count DESC
        """
        
        return await self.query(sql)
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _write_line(self, line: str):
        """Write InfluxDB line protocol data"""
        
        # Add timestamp (nanoseconds)
        import time
        timestamp_ns = int(time.time() * 1_000_000_000)
        line_with_ts = f"{line} {timestamp_ns}"
        
        # Send to ILP port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.ilp_port))
            sock.sendall((line_with_ts + "\n").encode())
        finally:
            sock.close()
    
    async def _execute_sql(self, sql: str):
        """Execute SQL statement"""
        
        response = await self.http_client.get(
            f"{self.http_url}/exec",
            params={"query": sql}
        )
        
        if response.status_code != 200:
            raise Exception(f"SQL execution failed: {response.text}")
        
        return response.json()
