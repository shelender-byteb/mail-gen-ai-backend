from operator import itemgetter
from fastapi import HTTPException,status
import asyncio
from pinecone import Pinecone

import traceback



from sqlalchemy import select, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback


from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore


from app.common.env_config import get_envs_setting


envs = get_envs_setting()




messages = [
    (
        "system",
        "You are a helpful assistant that explains the grammer of user sentence. Explain the user sentence.",
    ),
    ("human", "I love programming."),
]
# ai_msg = llm.invoke(messages)
# print(f"\n\nAI Message of Bedrock model is: {ai_msg.content}\n\n")


embeddings = OpenAIEmbeddings(model=envs.EMBEDDINGS_MODEL_NAME)

PINECONE_CLIENT = Pinecone(api_key=envs.PINECONE_API_KEY)
PINECONE_KB_INDEX_CLIENT = PINECONE_CLIENT.Index(name=envs.PINECONE_KNOWLEDGE_BASE_INDEX)
vectorstore = PineconeVectorStore(index=PINECONE_KB_INDEX_CLIENT, embedding=embeddings)
default_retriever = vectorstore.as_retriever(
            search_type='mmr',
            search_kwargs={
                "k": 10 ,
            }
)


async def _simple_prompt_assistant(llm, system_message: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_message,
            ),
            MessagesPlaceholder(variable_name="user_input"),
        ]
    )
    return prompt | llm







async def construct_kb_chain(LLM_ROLE, LLM_PROMPT, llm, chatbot_id: int, db_session, user_retriever):
    
    extract_input = RunnableLambda(lambda inputs: inputs['input'])



    output_parser = StrOutputParser()

    # main_chain = {
    #     "retrieved_context": retriever_chain,
    #     "input": extract_input,
    # } | prompt | llm | output_parser



    async def debug_retriever(query: str):
        try:
            print("\n=== Retriever Debug ===")
            print(f"Query: {query}")
            
            # docs = await default_retriever.ainvoke(query)
            # print(f"\n\nRetrieved Documents: {docs}")
            
            # # print(f"\n\nRetrieved Documents: {docs}")
            # for i, doc in enumerate(docs, 1):
            #     print(f"\n--- Document {i} ---")
            #     print(f"Content: {doc.page_content}")
            #     print(f"Metadata: {doc.metadata}")
            
            print("\n===================\n")
        except Exception as e:
            print(f"\nError in retriever is {str(e)}\n")
            traceback.print_exc()

    
    # async def topical_guardrail(inputs: dict) -> str:
    #     try:
    #         with get_openai_callback() as cb:
    #             moderation_result = await moderation_chain.ainvoke({"input": inputs["input"]})
    #             return moderation_result, cb.total_tokens
        
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Error processing request: {str(e)}"
    #         )
    
    async def get_chat_response(inputs: dict) -> str:
        try:
            with get_openai_callback() as cb:
                result =  await main_chain.ainvoke(inputs)
                return result, cb.total_tokens
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing request: {str(e)}"
            )
        
    # async def execute_chat_with_guardrail(inputs: dict) -> str:
    #     try:
    #         # Create parallel tasks
    #         await debug_retriever(inputs["input"])

    #         # topical_guardrail_task = asyncio.create_task(topical_guardrail(inputs))
    #         chat_task = asyncio.create_task(get_chat_response(inputs))

    #         while True:
    #             # done, _ = await asyncio.wait(
    #             #     [topical_guardrail_task, chat_task], 
    #             #     return_when=asyncio.FIRST_COMPLETED
    #             # )

    #             # if topical_guardrail_task in done:
    #             #     guardrail_result, moderation_tokens = topical_guardrail_task.result()
    #             #     # print(f"\n\nGuardrail result: {guardrail_result}\n\n")
    #             #     if guardrail_result.strip() != "ALLOWED":
    #             #         chat_task.cancel()
    #             #         return "I apologize, but I'm not permitted to discuss this topic. Please feel free to ask me something else that aligns with our usage policies.", moderation_tokens

    #             if chat_task in done:
    #                 chat_response, main_tokens = chat_task.result()
    #                 return chat_response, main_tokens
                
    #             await asyncio.sleep(0.1) 

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Error processing request: {str(e)}"
    #         )

    
    # return execute_chat_with_guardrail


