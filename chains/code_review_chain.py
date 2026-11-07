import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from prompts.code_review_prompt import review_promot
from models.schemas import Result
from dotenv import load_dotenv


load_dotenv()

def get_key():
    llm=ChatGroq(temperature=0.3 ,model="openai/gpt-oss-20b" , api_key=os.getenv("GROQ_API_KEY") )

    parser=PydanticOutputParser(pydantic_object=Result)

    prompt=review_promot()
    prompt=prompt.partial(format_instructions=parser.get_format_instructions())

    chain=prompt | llm | parser
    return chain