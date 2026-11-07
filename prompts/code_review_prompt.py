from langchain_core.prompts import ChatPromptTemplate

def review_promot():
    system_template= """أنت مهندس برمجيات خبير ومراجع اكواد متقدم.
    مهمتك هي مراجعة الكود البرمجي التالي وتحليله بدقة لاكتشاف الاخطاء,مشاكل الاداء,الثغرات الامنية,ومخالفات افضل الممارسات.
      يجب ان تقوم بإرجاع النتيجة حصرا بصيغة JSON صالحة تماما مع المخطط التالي.
        لا تقوم بإضافة اي نصوص او شروحات خارج هيكل JSON والشرح يكون بالعربي.
          
            تعليمات التنسيق: {format_instructions}  """


    human_template="""لغة البرمجة: {language}
    الكود المراد مراجعته: {code}"""

    prompt=ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human",human_template)

    ]) 
    return prompt