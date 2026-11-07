from pydantic import BaseModel,Field
from typing import List, Optional 



class Code(BaseModel):
    severity: str = Field(description=" مستوى الخطورة : Critical, High , Medium ,Low")
    category: str = Field(description="نوع المشكلة : Bug, Seurity, Performace, Best Practice",default=None)
    line: Optional[int] = Field(description=" رقم السطر التي توجد فيه المشكلة ")
    problem: str = Field(description="وش المشكلة باختصار")
    explanation: str = Field(description="شرح مفصل لسبب المشكلة")
    recommendation: str = Field(description="كيفية حل المشكلة")


class Result(BaseModel):
    summary: str = Field(description=" ملخص عام عن الكود المرفق")
    overall_score: int = Field(description="تقييم الكود من 100")
    issues: List[Code] = Field(description="قائمة بالمشاكل التي تم العثور عليها في الكود")
    improved_code: str = Field(description="نسخة محسنة ونظيفة من الكود الاصلي تحل جميع المشاكل")