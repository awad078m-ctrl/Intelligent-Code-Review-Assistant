import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st
from services.code_reviewer import process_code_review

st.set_page_config(page_title="Intelligent Code Reviewer", layout="wide")
st.title("🤖 Intelligent Code Review Assistant")

# --- تهيئة الجلسة والسجل الخاص بالمستخدم الحالي ---
if "session_history" not in st.session_state:
    st.session_state.session_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_language" not in st.session_state:
    st.session_state.current_language = "Python"

# الشريط الجانبي لعرض السجل الخاص بالجلسة الحالية
st.sidebar.header("📂 سجل مراجعات جلستك")

if st.session_state.session_history:
    for idx, item in enumerate(st.session_state.session_history):
        if st.sidebar.button(f"مراجعة #{idx+1} | {item['language']}", key=f"hist_btn_{idx}"):
            st.session_state.current_result = item["result"]
            st.session_state.current_language = item["language"]
else:
    st.sidebar.info("لا توجد مراجعات مسجلة في هذه الجلسة بعد.")

# خيارات الإدخال
language = st.selectbox(
    "اختر لغة البرمجة:",
    ["Python", "JavaScript", "Java", "C++", "HTML", "Other"],
    index=0
)

# ميزة رفع ملف برمجي أو نصي
uploaded_file = st.file_uploader(
    "أو ارفع ملف كود (اختياري):",
    type=["py", "js", "java", "cpp", "c", "h", "html", "css", "txt"]
)

uploaded_code = ""
if uploaded_file is not None:
    try:
        uploaded_code = uploaded_file.getvalue().decode("utf-8")
        st.success(f"تم تحميل الملف: {uploaded_file.name}")
    except Exception as e:
        st.error(f"تعذر قراءة الملف: {e}")

# إذا تم رفع ملف، يظهر محتواه تلقائياً في صندوق الكود لسهولة المراجعة أو التعديل
code_input = st.text_area(
    "أدخل الكود هنا أو عدّل محتوى الملف المرفوع:",
    value=uploaded_code if uploaded_code else "",
    height=250
)

if st.button("Review Code", type="primary"):
    final_code = code_input.strip()
    if not final_code:
        st.warning("الرجاء إدخال كود أو رفع ملف أولاً.")
    else:
        with st.spinner("جاري تحليل الكود وتقييمه..."):
            try:
                result = process_code_review(language, final_code)

                # تحديث النتيجة الحالية
                st.session_state.current_result = result
                st.session_state.current_language = language

                # إضافة النتيجة فوراً إلى سجل جلسة المستخدم الحالي
                st.session_state.session_history.append({
                    "language": language,
                    "result": result
                })

                st.success("تم تحليل الكود بنجاح وإضافته إلى السجل!")
            except Exception as e:
                st.error(f"فشل التحليل. تأكد من صحة API Key أو اتصال الإنترنت. التفاصيل: {str(e)}")

# عرض النتائج (سواء الجديدة أو المختارة من السجل)
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