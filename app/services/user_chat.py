import json, uuid
import time
import logging
from sqlalchemy.future import select
from fastapi import HTTPException,status, BackgroundTasks
from fastapi.responses import JSONResponse


from langchain_openai import OpenAIEmbeddings

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.common.env_config import get_envs_setting
# from app.utils.langchain_helper import _simple_prompt_assistant, construct_kb_chain, _load_last_10_messages

from langchain_openai import ChatOpenAI

from app.utils.prompt import PROMPT_TEMPLATE, prompt

logging.basicConfig(level=logging.INFO)
envs = get_envs_setting()

embeddings = OpenAIEmbeddings(model=envs.EMBEDDINGS_MODEL_NAME)

pinecone_client = Pinecone(api_key=envs.PINECONE_API_KEY)
vectorstore = PineconeVectorStore(
    index=pinecone_client.Index(envs.PINECONE_KNOWLEDGE_BASE_INDEX),
    embedding=embeddings
)


llm = ChatOpenAI(
    model_name='gpt-4o',
    temperature=0.7
)


# Base your implementation on these examples:
# {examples}


# PROMPT_TEMPLATE = """
# You are an expert web developer specializing in creating splash pages. 
# Generate a complete HTML/CSS code based on the user's description and selected style.

# Style type: {style_type}
# User description: {user_input}


# Guidelines:
# 1. Include ALL CSS in <style> tags
# 2. Use responsive design
# 3. Add subtle animations
# 4. Ensure color scheme matches the style type
# 5. Include a main headline, subheading, and CTA button
# 6. Make it a complete standalone HTML file

# """

async def generate_splash_page(query: str, style_type: str) -> str:
    """Generate HTML code for a splash page using RAG and LLMs"""
    try:

        print(f"Query is {query} and style type is {style_type}")

        # retriever = vectorstore.as_retriever(
        #     search_kwargs={
        #         "k": 3,
        #         "filter": {"style": style_type}
        #     }
        # )

        # docs = await retriever.ainvoke(query)
        # print(f"Docs retrived from retriever are: {docs}")
        # examples = "\n\n".join([doc.page_content for doc in docs])
        # print(f"Formatted docs from retriever are: {docs}")

        # prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        chain = prompt | llm

        response = await chain.ainvoke({
            "style_type": style_type,
            "user_input": query,
            # "examples": examples
        })

        print(f"\n\nResponse from chain is {response}\n")
        return response.content

    except Exception as e:
        print(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate splash page"
        )





async def get_chat_messagegs(thread_id, redis_store, llm=None):
    try:
       
        messages = await redis_store.lrange(str(f"conversation:{thread_id}"), 0, -1)
        print(f"\n\nMessages stored in redis are: {messages}\n\n")
        if not messages:
            # last_10_messages = await langchain_helper._load_last_10_messages(thread_id=data.id, db_session = session)
            # for message in last_10_messages:
            #     if isinstance(AIMessage, message):
            #         redis_store.rpush(str(data.id), json.dumps({"role": "ai", "message": message.content}))
            #     else:
            #         redis_store.rpush(str(data.id), json.dumps({"role": "human", "message": message.content}))
            
            # redis_store.expire(str(data.id), envs.TIME_TO_LIVE_IN_SECONDS)
            
            # current_time = time.time()  
            # redis_store.zadd("active_sessions", {str(data.id): current_time})
            return []
        
        return [json.loads(msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    



