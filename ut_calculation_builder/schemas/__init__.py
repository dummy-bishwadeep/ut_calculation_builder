from typing import Optional, Dict

from pydantic import BaseModel


class WidgetSaveRequest(BaseModel):
    dashboard_id: str
    type: Optional[str] = "dashboard"
    widget_data: Dict = {}
    project_id: str
    widget_id: Optional[str] = ""
    database: str = "kairos"