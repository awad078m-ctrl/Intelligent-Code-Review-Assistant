import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st
from database.database import init_db, all_review
from services.code_reviewer import process_code_review

init_db()

st.set_page_config(page_title="Intelligent Code Reviewer", layout="wide")
st.title("🤖 Intelligent Code Review Assistant")

# تهيئة الذاكرة المؤقتة لعرض النتائج (سواء الجديدة أو المسترجعة من السجل)
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_language" not in st.session_state:
    st.session_state.current_language = "Python"

st.sidebar.header("📂 سجل المراجعات السابقة")
history = all_review()

if history:
    for row in history:
        # row[0]: id, row[1]: language, row[2]: created_at, row[3]: review_result (json)
        review_id = row[0]
        lang = row[1]
        date_time = str(row[2])[:16]
        
        # زر لكل سجل قديم في الشريط الجانبي
        if st.sidebar.button(f"مراجعة #{review_id} | {lang}\n{date_time}", key=f"hist_{review_id}"):
            try:
                # تحويل النص المخزن بصيغة JSON إلى قاموس بيانات Python
                stored_data = json.loads(row[3])
                
                # استخدام Pydantic لضمان توافق الهيكل وتحويله لكائن (Object)
                from models.schemas import Result, Code
                # إعادة بناء الكائن ليطابق الهيكل البرمجي
                issues_list = [
                    Code(
                        severity=iss.get("severity", "Medium"),
                        category=iss.get("category", "General"),
                        problem=iss.get("problem", ""),
                        line=iss.get("line"),
                        explanation=iss.get("explanation", ""),
                        recommendation=iss.get("recommendation", "")
                    ) for iss in stored_data.get("issues", [])
                ]
                
                st.session_state.current_result = Result(
                    summary=stored_data.get("summary", ""),
                    overall_score=stored_data.get("overall_score", 0),
                    issues=issues_list,
                    improved_code=stored_data.get("improved_code", "")
                )
                st.session_state.current_language = lang
                st.rerun() # إعادة تحميل الصفحة لعرض السجل المختار
            except Exception as e:
                st.sidebar.error(f"خطأ في تحميل السجل: {e}")
else:
    st.sidebar.info("لا توجد مراجعات سابقة.")


language = st.selectbox("اختر لغة البرمجة:", ["Python", "JavaScript", "Java", "C++", "HTML", "Other"], index=0)
code_input = st.text_area("أدخل الكود هنا:", height=250)

if st.button("Review Code", type="primary"):
    if not code_input.strip():
        st.warning("الرجاء إدخال الكود أولاً.")
    else:
        with st.spinner("جاري تحليل الكود وتقييمه..."):
            try:
                result = process_code_review(language, code_input)
                # حفظ النتيجة الجديدة في الجلسة لعرضها
                st.session_state.current_result = result
                st.session_state.current_language = language
                st.success("تم تحليل الكود بنجاح!")
            except Exception as e:
                st.error(f"فشل التحليل. تأكد من صحة API Key أو اتصال الإنترنت. التفاصيل: {str(e)}")

# عرض النتائج (سواء تم إنشاؤها الآن أو تم جلبها من السجل التاريخي)
if st.session_state.current_result:
    result = st.session_state.current_result
    
    st.markdown("---")
    st.subheader("📊 ملخص المراجعة")
    st.write(result.summary)
    st.progress(result.overall_score / 100)
    st.write(f"**التقييم العام:** {result.overall_score}/100")
    
    st.subheader("⚠️ المشاكل المكتشفة")
    if result.issues:
        for issue in result.issues:
            icon = "🔴" if issue.severity == "Critical" else "🟠" if issue.severity == "High" else "🟡"
            with st.expander(f"{icon} [{issue.severity}] {issue.category} - {issue.problem}"):
                st.write(f"**السطر:** {issue.line if issue.line else 'غير محدد'}")
                st.write(f"**الشرح:** {issue.explanation}")
                st.write(f"**الحل المقترح:** {issue.recommendation}")
    else:
        st.info("لم يتم العثور على مشاكل واضحة في الكود! عمل ممتاز.")

    st.subheader("✨ الكود المحسن")
    st.code(result.improved_code, language=st.session_state.current_language.lower())