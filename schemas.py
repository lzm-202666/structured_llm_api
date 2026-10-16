from pydantic import BaseModel,Field

class ChatRequest(BaseModel):
    user_id: str = Field(...,description="用户ID")
    message: str = Field(...,min_length=1,description="用户消息")

class StructuredOutput(BaseModel):
    title: str = Field(...,description="根据用户输入提取的标题")
    keywords: list[str] = Field(...,description="提取出的关键词列表")


