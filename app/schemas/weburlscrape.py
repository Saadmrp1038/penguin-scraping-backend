import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
    
    
class webUrlTrain(BaseModel):
    id: str
    url: str