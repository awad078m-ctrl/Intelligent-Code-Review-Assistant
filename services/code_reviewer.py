from chains.code_review_chain import get_key
from database.database import save_review

def process_code_review(language: str , code: str):
    try:
        chain=get_key()
        result=chain.invoke({"language": language , "code": code})
        save_review(language , code , result.model_dump())
        return result
    except Exception as e:
        raise Exception(f"حدث خطأ أثناء تحليل الكود: {str(e)}")
