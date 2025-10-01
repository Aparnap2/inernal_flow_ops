from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["API"])

# Mock data for testing
MOCK_RUNS = [
    {
        "id": "run_001",
        "workflow_type": "company_intake",
        "status": "completed",
        "created_at": "2025-01-01T10:00:00Z",
        "completed_at": "2025-01-01T10:05:00Z",
        "metadata": {"company_name": "Acme Corp", "industry": "Technology"}
    },
    {
        "id": "run_002", 
        "workflow_type": "deal_stage_kickoff",
        "status": "pending_approval",
        "created_at": "2025-01-01T11:00:00Z",
        "metadata": {"deal_amount": 50000, "stage": "proposal"}
    }
]

MOCK_APPROVALS = [
    {
        "id": "approval_001",
        "run_id": "run_002",
        "type": "deal_approval",
        "status": "pending",
        "created_at": "2025-01-01T11:00:00Z",
        "context": {"deal_amount": 50000, "requires_procurement": True},
        "policy_snapshot": {"max_auto_approve": 25000}
    }
]

MOCK_EXCEPTIONS = [
    {
        "id": "exception_001",
        "run_id": "run_003",
        "type": "data_quality",
        "status": "open",
        "created_at": "2025-01-01T12:00:00Z",
        "error_message": "Missing required field: company_website",
        "suggested_fix": "Contact data source to provide website URL"
    }
]

@router.get("/runs")
async def get_runs(limit: int = 20):
    return {"runs": MOCK_RUNS[:limit], "total": len(MOCK_RUNS)}

@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    run = next((r for r in MOCK_RUNS if r["id"] == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/approvals/pending")
async def get_pending_approvals():
    pending = [a for a in MOCK_APPROVALS if a["status"] == "pending"]
    return {"approvals": pending, "total": len(pending)}

@router.patch("/approvals/{approval_id}/decision")
async def make_approval_decision(approval_id: str, decision: Dict[str, Any]):
    approval = next((a for a in MOCK_APPROVALS if a["id"] == approval_id), None)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    approval["status"] = "approved" if decision.get("approved") else "rejected"
    approval["decision_at"] = "2025-01-01T13:00:00Z"
    approval["decision_by"] = decision.get("user_id", "admin")
    approval["comments"] = decision.get("comments", "")
    
    return {"message": "Decision recorded", "approval": approval}

@router.get("/exceptions/open")
async def get_open_exceptions():
    open_exceptions = [e for e in MOCK_EXCEPTIONS if e["status"] == "open"]
    return {"exceptions": open_exceptions, "total": len(open_exceptions)}

@router.patch("/exceptions/{exception_id}/resolve")
async def resolve_exception(exception_id: str, resolution: Dict[str, Any]):
    exception = next((e for e in MOCK_EXCEPTIONS if e["id"] == exception_id), None)
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    
    exception["status"] = "resolved"
    exception["resolved_at"] = "2025-01-01T14:00:00Z"
    exception["resolution"] = resolution.get("resolution", "")
    
    return {"message": "Exception resolved", "exception": exception}

@router.get("/users/me")
async def get_current_user():
    return {
        "id": 1,
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "is_active": True
    }
