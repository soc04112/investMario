from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.agent.agent_runner import run_agent
from app.auth.jwt_user import get_current_user 

router = APIRouter(prefix="/agent", tags=["agent"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    tool_used: str | None = None
@router.post("/chat", response_model=ChatResponse)
async def chat_agent(
    req: ChatRequest,
    user=Depends(get_current_user)  # 🔐 여기서 userid 확보
):
    """
    user = {
      "sub": userid,
      "email": ...
    }
    """

    userid = user["sub"]

    result = await run_agent(
        user_message=req.message,
        userid=userid
    )

    return ChatResponse(
        answer=result["answer"],
        tool_used=result.get("tool")
    )
