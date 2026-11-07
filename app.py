from dotenv import load_dotenv
import streamlit as st
from database.database import init_db, all_review
from services.code_reviewer import process_code_review

load_dotenv(override=True)


init_db()

st.set_page_config(page_title="Intelligent Code Reviewer", layout="wide")
st.title("🤖 Intelligent Code Review Assistant")

st.sidebar.header("سجل المراجعات السابقة")
history = all_review()

if history:
    for row in history:
        st.sidebar.text(f"مراجعة #{row[0]} | {row[1]}\n{row[2][:16]}")
        st.sidebar.markdown("---")
else:
    st.sidebar.info("لا توجد مراجعات سابقة.")


language = st.selectbox("اختر لغة البرمجة:", ["Python", "JavaScript", "Java", "C++", "HTML", "Other"])
code_input = st.text_area("أدخل الكود هنا:", height=250)

if st.button("Review Code", type="primary"):
    if not code_input.strip():
        st.warning("الرجاء إدخال الكود أولاً.")
    else:
        with st.spinner("جاري تحليل الكود وتقييمه..."):
            try:
                result = process_code_review(language, code_input)
                            
                st.success("تم تحليل الكود بنجاح!")
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
                    st.code(result.improved_code, language=language.lower())
            except Exception as e:
                st.error(f"فشل التحليل. تأكد من صحة API Key أو اتصال الإنترنت. التفاصيل: {str(e)}")



