"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connector Deployment API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import asyncio

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


class DeployConnectorRequest(BaseModel):
    entity_id: str
    integration_type: str
    credentials: Optional[Dict[str, Any]] = None


class DeployConnectorResponse(BaseModel):
    connector_id: str
    status: str
    message: str
    deployment_url: Optional[str] = None


class ConnectorStatusResponse(BaseModel):
    connector_id: str
    status: str  # 'deploying', 'running', 'stopped', 'error'
    health: str  # 'healthy', 'degraded', 'down'
    uptime_seconds: int
    messages_processed: int
    error_count: int


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deploy a new connector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/deploy", response_model=DeployConnectorResponse)
async def deploy_connector(req: DeployConnectorRequest):
    """
    Deploy a new connector to AckwardRootsInc
    
    Flow:
    1. Generate connector code (if needed)
    2. Deploy to AckwardRootsInc
    3. Inject vault credentials
    4. Start streaming to Kafka
    """
    
    connector_id = f"{req.entity_id}_{req.integration_type}"
    
    # Check if connector already exists
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://ackwardroots:8003/api/connectors/{connector_id}"
            )
            if response.status_code == 200:
                return DeployConnectorResponse(
                    connector_id=connector_id,
                    status="already_deployed",
                    message=f"Connector {connector_id} is already deployed",
                    deployment_url=f"http://ackwardroots:8003/connectors/{connector_id}"
                )
    except:
        pass
    
    # Deploy new connector to AckwardRootsInc
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://ackwardroots:8003/api/connectors/deploy",
                json={
                    "connector_id": connector_id,
                    "entity_id": req.entity_id,
                    "integration_type": req.integration_type,
                    "vault_path": f"{req.entity_id}/{req.integration_type}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return DeployConnectorResponse(
                    connector_id=connector_id,
                    status="deployed",
                    message=f"Connector deployed successfully",
                    deployment_url=data.get("url")
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to deploy connector: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Deployment timeout - connector may still be deploying"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {str(e)}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Get connector status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/{connector_id}/status", response_model=ConnectorStatusResponse)
async def get_connector_status(connector_id: str):
    """Get real-time status of a connector from AckwardRootsInc"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://ackwardroots:8003/api/connectors/{connector_id}/status"
            )
            
            if response.status_code == 200:
                return ConnectorStatusResponse(**response.json())
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Connector not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get status: {response.text}"
                )
                
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="AckwardRootsInc service unavailable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stop a connector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/{connector_id}/stop")
async def stop_connector(connector_id: str):
    """Stop a running connector"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://ackwardroots:8003/api/connectors/{connector_id}/stop"
            )
            
            if response.status_code == 200:
                return {"message": "Connector stopped successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to stop connector: {response.text}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop connector: {str(e)}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start a connector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/{connector_id}/start")
async def start_connector(connector_id: str):
    """Start a stopped connector"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://ackwardroots:8003/api/connectors/{connector_id}/start"
            )
            
            if response.status_code == 200:
                return {"message": "Connector started successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to start connector: {response.text}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start connector: {str(e)}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# List all connectors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/list")
async def list_connectors(entity_id: Optional[str] = None):
    """List all deployed connectors, optionally filtered by entity"""
    
    try:
        async with httpx.AsyncClient() as client:
            params = {"entity_id": entity_id} if entity_id else {}
            response = await client.get(
                "http://ackwardroots:8003/api/connectors",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to list connectors: {response.text}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list connectors: {str(e)}"
        )
