# app/services/email_generator.ts
import logging
import re
from langchain_core.prompts import ChatPromptTemplate
from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from langchain_openai import ChatOpenAI
from fastapi import HTTPException, status

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='gpt-4o',
    temperature=0.7
)

# llm = ChatOpenAI(
#     model_name='o3-mini'
# )



EMAIL_GENERATION_TEMPLATE = """
You are an expert email marketing specialist who creates visually appealing, engaging, and conversion-focused email advertisements.

Your task is to generate a high-quality HTML email advertisement based on the website content and user prompt provided below.

WEBSITE INFORMATION:
Website URL: {website_url}
Website Content: 
{website_content}

USER PROMPT:
{user_prompt}

GUIDELINES:
1. Create a compelling subject line that entices recipients to open the email
2. Use a friendly, exciting tone that matches the company's industry and branding
3. Include a clear value proposition early in the email
4. Be highly creative with the email structure
5. Use emojis strategically to make the email eye-catching
6. Incorporate varied formatting including headings, paragraphs, and feature lists
7. Create a VISUALLY APPEALING email that stands out in an inbox
8. Make the tone engaging and energetic 
9. Add a strong call-to-action button that directs recipients to the website
10. Keep the email concise (200-250 words maximum)
11. Include the provided website URL as a clickable link in the call-to-action
12. Use only the provided website URL {website_url} in the email as the primary link for all call-to-actions, not any links from the scraped content
13. CRITICAL: Create unique, VISUALLY STUNNING designs for each email with creative layouts, color schemes, and formatting
14. CRITICAL: Ensure ALL buttons, links, and call-to-actions redirect to the website URL using target="_blank" to open in a new page
15. CRITICAL: - DO NOT include any footer sections,  copyright notices, or footer content in your output.
16. IMPORTANT: GIVE RESPONSE IN COMPLETE HTML FORMAT WITH CSS STYLING THAT WORKS ACROSS ALL EMAIL CLIENTS, ESPECIALLY GMAIL
17. CRITICAL: For Gmail compatibility while maintaining visual excellence:
    - Use inline CSS only on each HTML element
    - Create sophisticated designs using table-based layouts (not div-based)
    - Use creative background colors, borders, and spacing for visual appeal
    - Implement attention-grabbing button designs with inline CSS
    - Avoid CSS properties that Gmail doesn't support (like position:absolute, float, etc.)
    - Keep image dimensions explicitly defined with width and height attributes
    - Use full HTML doctype and structure
    - Use innovative design elements and styling techniques to create the best possible email layout.
18. CRITICAL: Your goal is to create the most visually impressive email possible while ensuring Gmail compatibility



Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
Remember to adapt your design to match the brand's style and the purpose of the email. 
"""


EMAIL_REFINEMENT_TEMPLATE = """
You are an expert email marketing specialist who helps refine and improve email advertisements.

Your task is to refine the existing HTML email advertisement based on the user's feedback.

ORIGINAL EMAIL:
{previous_email}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

GUIDELINES:
1. Maintain the original structure and HTML format of the email
2. Make only the changes requested by the user
3. Keep the overall tone consistent with the brand while maintaining an exciting, energetic style
4. Maintain a clear call-to-action that links to the provided website URL. Update the website URL if requested. by user.
5. Ensure the email remains concise and focused
6. Preserve or enhance the styling of the original email unless otherwise specified by the user

THESE WERE THE ORIGINAL GUIDELINES FOR PREVIOUSLY GENERATED EMAIL (THEY ARE JUST FOR YOUR REFERRENCE AND GUIDANCE):
GUIDELINES GIVEM WHILE GENERATING PREVIOUS EMAIL:
1. Create a compelling subject line that entices recipients to open the email
2. Use a friendly, professional tone that matches the company's industry and branding
3. Include a clear value proposition early in the email
4. Be highly creative with the email structure
5. Use emojis strategically to make the email eye-catching
6. Incorporate varied formatting including headings, paragraphs, and feature lists
7. Create a visually appealing email that stands out in an inbox
8. Make the tone engaging and energetic while maintaining professionalism 
9. Add a strong call-to-action button that directs recipients to the website
10. Keep the email concise (200-250 words maximum)
11. Include the provided website URL as a clickable link in the call-to-action
12. Use only the provided website URL in the email as the primary link for all call-to-actions, not any links from the scraped content
13. CRITICAL: Create unique, original designs for each email
14. CRITICAL: Ensure ALL buttons, links, and call-to-actions redirect to the website URL using target="_blank" to open in a new page
15. IMPORTANT: GIVE RESPONSE IN COMPLETE HTML FORMAT WITH CSS STYLING THAT WORKS ACROSS ALL EMAIL CLIENTS, ESPECIALLY GMAIL
16. CRITICAL: For Gmail compatibility:
    - Use inline CSS only (avoid using <style> tags in the head)
    - Avoid complex CSS selectors and properties
    - Use simple table-based layouts instead of div-based layouts
    - Avoid CSS properties that Gmail doesn't support (like position:absolute, float, etc.)
    - Limit CSS to well-supported properties (color, font-size, background-color, etc.)
    - Use basic HTML formatting tags (<b>, <i>, <strong>, etc.) for text formatting
    - Keep image dimensions explicitly defined with width and height attributes
    - Use full HTML doctype and structure
16. Test all links to ensure they work properly with the target="_blank" attribute
17. CRITICAL: Your goal is to create the most visually impressive email possible while ensuring Gmail compatibility


Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""



async def generate_email_advertisement(
    prompt: str,
    website_url: str,
    operation: str = "generate",
    previous_email: str = None
) -> str:
    """
    Generate or refine an email advertisement based on website content
    
    Args:
        prompt: User prompt/instructions
        website_url: URL of the website to scrape
        operation: 'generate' for new email or 'refine' to update existing
        previous_email: Previous email content (for refinement)
        
    Returns:
        str: Generated or refined email content
    """
    try:
        logging.info(f"Email generation request - Operation: {operation}, URL: {website_url}")
        
        if operation == "refine" and previous_email:
            print(f"Operation is refine so updating the existing email {previous_email}")
            refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
            chain = refinement_prompt | llm
            
            response = await chain.ainvoke({
                "user_prompt": prompt,
                "previous_email": previous_email
            })

            response = extract_pure_html(response.content)
            return response
            
            # return response.content
        
        # For new email generation, scrape the website first

        print(f"Operation is generate.....")

        website_data = await scrape_website(website_url)
        
        if 'error' in website_data:
            logging.error(f"Website scraping error: {website_data['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape website: {website_data['error']}"
            )
        
        generation_prompt = ChatPromptTemplate.from_template(EMAIL_GENERATION_TEMPLATE)
        chain = generation_prompt | llm

        # Also update in the generate_email_advertisement function:
        response = await chain.ainvoke({
            "user_prompt": prompt,
            "website_url": website_url,
            "website_content": website_data.get('content', '')
        })

        response = extract_pure_html(response.content)
        return response
        
        # return response.content
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logging.error(f"Email generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email advertisement: {str(e)}"
        )
    

def extract_pure_html(response_content: str) -> str:
    # Regex to find content between <!DOCTYPE html> and </html>
    html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', response_content, re.DOTALL | re.IGNORECASE)
    if html_match:
        logging.info("Extracted pure HTML")
        return html_match.group(1)

    else:
        logging.warning(f"Could not extract pure HTML. Full response: {response_content}")
        return response_content
    






# import logging
# import re
# from langchain_core.prompts import ChatPromptTemplate
# from app.utils.website_scraper import scrape_website
# from app.common.env_config import get_envs_setting
# from langchain_openai import ChatOpenAI
# from fastapi import HTTPException, status

# # New imports for dynamic DB loading:
# from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.common.database_config import get_async_db
# from app.models.model_config import ModelConfig
# from app.models.template import Template
# from app.enums.model_type import ModelType
# from app.enums.template_type import TemplateType

# envs = get_envs_setting()

# async def generate_email_advertisement(
#     prompt: str,
#     website_url: str,
#     operation: str = "generate",
#     previous_email: str = None
# ) -> str:
#     """
#     Generate or refine an email advertisement based on website content.
#     Dynamically loads LLM config and prompt template from the database.
#     """
#     try:
#         logging.info(f"Email generation request - Operation: {operation}, URL: {website_url}")
        
#         # Use an async session to fetch configs from DB
#         async with get_async_db() as session:
#             # 1. Fetch email model configuration
#             result = await session.execute(
#                 select(ModelConfig).where(ModelConfig.model_type == ModelType.EMAIL.value)
#             )
#             email_model_config = result.scalars().first()
#             if not email_model_config:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No model configuration found for email"
#                 )
#             llm = ChatOpenAI(
#                 model_name=email_model_config.model_name,
#                 temperature=email_model_config.temperature
#             )
            
#             # 2. Choose template based on operation
#             if operation == "refine" and previous_email:
#                 # Use email refinement template
#                 result = await session.execute(
#                     select(Template).where(Template.template_type == TemplateType.EMAIL_REFINEMENT.value)
#                 )
#                 template_record = result.scalars().first()
#                 if not template_record:
#                     raise HTTPException(
#                         status_code=status.HTTP_404_NOT_FOUND,
#                         detail="No email refinement template found"
#                     )
#             else:
#                 # Use email generation template
#                 # First, scrape the website (only for new email generation)
#                 website_data = await scrape_website(website_url)
#                 if 'error' in website_data:
#                     logging.error(f"Website scraping error: {website_data['error']}")
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"Failed to scrape website: {website_data['error']}"
#                     )
#                 result = await session.execute(
#                     select(Template).where(Template.template_type == TemplateType.EMAIL_GENERATION.value)
#                 )
#                 template_record = result.scalars().first()
#                 if not template_record:
#                     raise HTTPException(
#                         status_code=status.HTTP_404_NOT_FOUND,
#                         detail="No email generation template found"
#                     )
            
#             # 3. Build the prompt template from DB content
#             current_prompt = ChatPromptTemplate.from_template(template_record.content)
#             chain = current_prompt | llm
            
#             # 4. Invoke the chain based on operation
#             if operation == "refine" and previous_email:
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "previous_email": previous_email
#                 })
#             else:
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "website_url": website_url,
#                     "website_content": website_data.get('content', '')
#                 })
            
#             response_content = extract_pure_html(response.content)
#             return response_content
        
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging.error(f"Email generation failed: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate email advertisement: {str(e)}"
#         )

# def extract_pure_html(response_content: str) -> str:
#     # Regex to find content between <!DOCTYPE html> and </html>
#     html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', response_content, re.DOTALL | re.IGNORECASE)
#     if html_match:
#         logging.info("Extracted pure HTML")
#         return html_match.group(1)
#     else:
#         logging.warning(f"Could not extract pure HTML. Full response: {response_content}")
#         return response_content
