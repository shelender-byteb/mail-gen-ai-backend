# app/services/email_generator.ts
import logging
import re
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from fastapi import HTTPException, status

from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from app.schemas.request.splash_page import Operation, EmailStyle

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='o3-mini'
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


EMAIL_PROFESSIONAL_TEMPLATE = """
Write an HTML email ad that reliably lands in Gmail’s Primary inbox.

SUBJECT LINE RULES:

- Use all lowercase.
- Use only one word, or one word with ~FIRSTNAME~, or just ~FIRSTNAME~.
- No punctuation, no title casing, no emojis.
- Personalization (~FIRSTNAME~) may appear before or after the word.
- Do not use subject lines not confirmed to work.

WORKING SUBJECT LINES:

question  
really  
seriously  
maybe  
unsure  
note  
this  
try  
error  
thoughts  
oops  
almost  
perfect  
~FIRSTNAME~  
question ~FIRSTNAME~  
~FIRSTNAME~ question  
try ~FIRSTNAME~  
~FIRSTNAME~ try  
this ~FIRSTNAME~  
~FIRSTNAME~ this  
thoughts ~FIRSTNAME~  
~FIRSTNAME~ thoughts  
maybe ~FIRSTNAME~  
~FIRSTNAME~ maybe  
error ~FIRSTNAME~  
~FIRSTNAME~ error  
almost ~FIRSTNAME~  
~FIRSTNAME~ almost  
oops ~FIRSTNAME~  
~FIRSTNAME~ oops  
perfect ~FIRSTNAME~  
~FIRSTNAME~ perfect

EMAIL BODY RULES:

- Use only <p> tags with inline styles like this:  
  <p style="font-size:17px;">Your sentence here.</p>

- Do not include: <style>, <head>, <body>, <div>, <span>, or any other tags.

- Do not include preheader filler — the system already adds it.

GREETING:

- Start with a casual, lowercase personalized greeting. Examples:  
  <p style="font-size:17px;">Hey ~FIRSTNAME~</p>  
  <p style="font-size:17px;">hi ~FIRSTNAME~</p>  
  <p style="font-size:17px;">alright ~FIRSTNAME~</p>  
  <p style="font-size:17px;">~FIRSTNAME~</p>

TONE & STYLE:

- Keep the tone friendly, natural, and unscripted — like a message from a friend.
- Use short sentences, occasional rambling or pause, and light human errors.
- Rotate tone (curious, skeptical, chill, humorous, reflective).
- Keep message short — 2-3 sentences max.

HUMAN-LIKE ERROR RULES:

✅ Include exactly one straight apostrophe (')  
✅ Include one word that’s missing its apostrophe (like dont, isnt, thats)  
❌ Do not use any curly apostrophes (’)  
❌ Do not use em dashes (—)

LINK RULES:

- Include one or two raw links mid-sentence only.
- Never place links on their own line.
- Never use buttons or phrases like "click here."

✅ GOOD:  
<p style="font-size:17px;">...ran into this: https://example.com</p>

🚫 BAD:  
<p style="font-size:17px;">https://example.com</p>  
<p style="font-size:17px;">Click here now!</p>

EMOJI RULE (optional):

- Use only one emoji if it fits naturally.
- Use HTML code like &#128514;
- Place mid-sentence or at end of sentence (never near a link)

SIGN-OFF:

End with a simple first-name sign-off:  
<p style="font-size:17px;">Ben</p>  
<br><br><br>

WEBSITE INFORMATION:
Website URL: {website_url}
Website Content:
{website_content}

USER PROMPT:
{user_prompt}

Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""

EMAIL_PROFESSIONAL_REFINEMENT_TEMPLATE = """
You are an expert email marketing specialist who refines professional, inbox-friendly emails.

Your task is to refine the existing professional HTML email advertisement based on the user's feedback. Follow these guidelines:

GUIDELINES:
1. Keep the tone friendly, personal, and conversational.
2. Maintain a story-based narrative without promotional language.
3. Use minimal formatting: plain paragraphs only, without buttons, images, or bold call-to-actions.
4. Limit links to no more than 1–2, ensuring they appear as natural, readable URLs.
5. Avoid emojis, buzzwords, and urgency phrases.
6. Include a preheader filler using a hidden div with non-breaking spaces.
7. Use simple inline CSS only if necessary.
8. Conclude with a personal sign-off (only a name, no titles or corporate info).
9. Do not include logos, graphics, or tracking pixels.
10. Maintain the original HTML structure as much as possible, making only the changes requested.
11. Use the provided website URL as the primary link wherever applicable.

ORIGINAL EMAIL:
{previous_email}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""


async def generate_email_advertisement(
    prompt: str,
    website_url: str,
    operation: Operation,
    email_style: EmailStyle,
    previous_email: str = None
) -> str:
    """
    Generate or refine an email advertisement based on website content
    
    Args:
        prompt: User prompt/instructions
        website_url: URL of the website to scrape
        operation: 'generate' for new email or 'refine' to update existing
        email_style: Style of the email (professional/salesy)
        previous_email: Previous email content (for refinement)
        
    Returns:
        str: Generated or refined email content
    """
    try:
        logging.info(f"Email generation request - Operation: {operation}, URL: {website_url}, Style: {email_style}")
        
        if email_style == "professional":
            if operation == "refine" and previous_email:
                logging.info("Using professional refinement template")
                refinement_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_REFINEMENT_TEMPLATE)
                chain = refinement_prompt | llm
                
                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "previous_email": previous_email
                })
                
                response = extract_pure_html(response.content)
                return response
            else:
                logging.info("Using professional generation template")
                website_data = await scrape_website(website_url)
                
                if 'error' in website_data:
                    logging.error(f"Website scraping error: {website_data['error']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to scrape website: {website_data['error']}"
                    )
                
                generation_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_TEMPLATE)
                chain = generation_prompt | llm
                
                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "website_url": website_url,
                    "website_content": website_data.get('content', '')
                })
                
                response = extract_pure_html(response.content)
                return response
        else:
            if operation == "refine" and previous_email:
                logging.info("Using regular refinement template")
                refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
                chain = refinement_prompt | llm
                
                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "previous_email": previous_email
                })
                
                response = extract_pure_html(response.content)
                return response
            else:
                logging.info("Using regular generation template")
                website_data = await scrape_website(website_url)
                
                if 'error' in website_data:
                    logging.error(f"Website scraping error: {website_data['error']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to scrape website: {website_data['error']}"
                    )
                
                generation_prompt = ChatPromptTemplate.from_template(EMAIL_GENERATION_TEMPLATE)
                chain = generation_prompt | llm
                
                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "website_url": website_url,
                    "website_content": website_data.get('content', '')
                })
                
                response = extract_pure_html(response.content)
                return response
        
        
    except HTTPException as e:
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
