"""
GPU Scheduler - Allocate and schedule GPU resources

The Conductor's timing: When and where each instrument plays
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import asyncio

class GPUType(Enum):
    A100 = "a100"           # 40GB VRAM, best for training
    RTX_4090 = "rtx_4090"   # 24GB VRAM, best for inference/rendering
    T4 = "t4"               # 16GB VRAM, cheap batch processing

class Priority(Enum):
    REALTIME = 0    # User waiting (< 5 sec)
    HIGH = 1        # Important (< 1 min)
    MEDIUM = 2      # Can wait (< 5 min)
    BATCH = 3       # Scheduled (hours)

class GPUScheduler:
    """
    Manages GPU allocation and job scheduling across Theta cluster
    """
    
    def __init__(self):
        self.job_queue = {
            Priority.REALTIME: [],
            Priority.HIGH: [],
            Priority.MEDIUM: [],
            Priority.BATCH: []
        }
        self.active_jobs = {}
        self.gpu_pool = self._initialize_gpu_pool()
    
    async def schedule(
        self,
        job_type: str,
        params: Dict[str, Any],
        gpu_type: GPUType,
        model: Optional[Dict] = None,
        priority: Priority = Priority.MEDIUM,
        user_id: str = None
    ) -> 'JobHandle':
        """
        Schedule a GPU job
        Returns job handle for tracking
        """
        
        job = {
            'id': self._generate_job_id(),
            'type': job_type,
            'params': params,
            'gpu_type': gpu_type,
            'model': model,
            'priority': priority,
            'user_id': user_id,
            'created_at': datetime.now(),
            'status': 'queued'
        }
        
        # Add to appropriate queue
        self.job_queue[priority].append(job)
        
        # Try to execute immediately if GPU available
        await self._try_execute_next()
        
        # Calculate queue position
        queue_position = self._calculate_queue_position(job)
        
        return JobHandle(
            id=job['id'],
            status='queued',
            queue_position=queue_position,
            estimated_start=self._estimate_start_time(job)
        )
    
    async def allocate_gpu(self, gpu_type: GPUType, count: int = 1) -> Optional[List[str]]:
        """
        Allocate GPU(s) from pool
        Returns GPU IDs if available
        """
        
        available = [
            gpu_id for gpu_id, gpu in self.gpu_pool.items()
            if gpu['type'] == gpu_type.value and gpu['status'] == 'available'
        ]
        
        if len(available) >= count:
            allocated = available[:count]
            
            # Mark as in use
            for gpu_id in allocated:
                self.gpu_pool[gpu_id]['status'] = 'in_use'
            
            return allocated
        
        return None
    
    async def _try_execute_next(self):
        """
        Try to execute the next highest priority job
        Called whenever GPU becomes available
        """
        
        # Check queues in priority order
        for priority in [Priority.REALTIME, Priority.HIGH, Priority.MEDIUM, Priority.BATCH]:
            if self.job_queue[priority]:
                job = self.job_queue[priority][0]
                
                # Try to allocate GPU
                gpus = await self.allocate_gpu(GPUType(job['gpu_type'].value))
                
                if gpus:
                    # Remove from queue
                    self.job_queue[priority].pop(0)
                    
                    # Execute job
                    await self._execute_job(job, gpus)
                    break
    
    async def _execute_job(self, job: Dict, gpus: List[str]):
        """
        Execute job on allocated GPUs
        """
        
        job['status'] = 'running'
        job['gpus'] = gpus
        job['started_at'] = datetime.now()
        
        self.active_jobs[job['id']] = job
        
        # TODO: Actually execute on Theta EdgeCloud
        # For now, simulate
        await asyncio.sleep(2)  # Simulate work
        
        # Complete job
        job['status'] = 'completed'
        job['completed_at'] = datetime.now()
        
        # Free GPUs
        for gpu_id in gpus:
            self.gpu_pool[gpu_id]['status'] = 'available'
        
        # Try to execute next job
        await self._try_execute_next()
    
    def _initialize_gpu_pool(self) -> Dict[str, Dict]:
        """
        Initialize GPU pool
        TODO: Query actual Theta cluster
        """
        return {
            f"a100_{i}": {'type': 'a100', 'status': 'available'} 
            for i in range(8)
        } | {
            f"rtx4090_{i}": {'type': 'rtx_4090', 'status': 'available'} 
            for i in range(12)
        } | {
            f"t4_{i}": {'type': 't4', 'status': 'available'} 
            for i in range(20)
        }
    
    def _calculate_queue_position(self, job: Dict) -> int:
        """
        Calculate position in queue
        """
        position = 1
        for priority in [Priority.REALTIME, Priority.HIGH, Priority.MEDIUM, Priority.BATCH]:
            if priority.value < job['priority'].value:
                position += len(self.job_queue[priority])
            elif priority == job['priority']:
                position += self.job_queue[priority].index(job)
                break
        
        return position
    
    def _estimate_start_time(self, job: Dict) -> datetime:
        """
        Estimate when this job will start
        Based on queue position and average job duration
        """
        queue_position = self._calculate_queue_position(job)
        avg_job_duration = 60  # 1 minute average
        
        return datetime.now() + timedelta(seconds=queue_position * avg_job_duration)
    
    def _generate_job_id(self) -> str:
        """
        Generate unique job ID
        """
        import uuid
        return f"job_{uuid.uuid4().hex[:12]}"


class JobHandle:
    """
    Handle for tracking a job
    """
    def __init__(self, id: str, status: str, queue_position: int, estimated_start: datetime):
        self.id = id
        self.status = status
        self.queue_position = queue_position
        self.estimated_start = estimated_start

