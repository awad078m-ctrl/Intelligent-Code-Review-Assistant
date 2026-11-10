import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

import streamlit as st
from services.code_reviewer import process_code_review

st.set_page_config(page_title="Intelligent Code Reviewer", layout="wide")
st.title("🤖 Intelligent Code Review Assistant")

# --- عزل الجلسات: تهيئة الذاكرة والسجل الخاص بهذا المستخدم فقط ---
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_language" not in st.session_state:
    st.session_state.current_language = "Python"
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# عرض سجل الجلسة الخاصة بالمستخدم الحالي فقط في الشريط الجانبي
st.sidebar.header("📂 سجل مراجعات جلستك")
if st.session_state.session_history:
    for idx, item in enumerate(st.session_state.session_history):
        # زر لكل مراجعة تمت في هذه الجلسة فقط
        if st.sidebar.button(f"مراجعة #{idx+1} | {item['language']}", key=f"sess_hist_{idx}"):
            st.session_state.current_result = item["result"]
            st.session_state.current_language = item["language"]
            st.rerun()
else:
    st.sidebar.info("لا توجد مراجعات مسجلة في هذه الجلسة بعد.")

# خيارات الإدخال
language = st.selectbox("اختر لغة البرمجة:", ["Python", "JavaScript", "Java", "C++", "HTML", "Other"], index=0)
code_input = st.text_area("أدخل الكود هنا:", height=250)

if st.button("Review Code", type="primary"):
    if not code_input.strip():
        st.warning("الرجاء إدخال الكود أولاً.")
    else:
        with st.spinner("جاري تحليل الكود وتقييمه..."):
            try:
                result = process_code_review(language, code_input)
                
                # تخزين النتيجة في الجلسة الحالية وعرضها فوراً للمستخدم فقط
                st.session_state.current_result = result
                st.session_state.current_language = language
                
                # إضافة النتيجة إلى سجل جلسة المستخدم الحالي
                st.session_state.session_history.append({
                    "language": language,
                    "result": result
                })
                
                st.success("تم تحليل الكود بنجاح!")
            except Exception as e:
                st.error(f"فشل التحليل. تأكد من صحة API Key أو اتصال الإنترنت. التفاصيل: {str(e)}")

# عرض النتائج الخاصة بالمستخدم الحالي
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