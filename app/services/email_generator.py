# app/services/email_generator.ts
import logging
from langchain_core.prompts import ChatPromptTemplate
from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from langchain_openai import ChatOpenAI
from fastapi import HTTPException, status

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='gpt-4o',
    temperature=0.5
)


# Update in app/services/email_generator.ts - modify EMAIL_GENERATION_TEMPLATE

EMAIL_GENERATION_TEMPLATE = """
You are an expert email marketing specialist who creates compelling, conversion-focused email advertisements.

Your task is to generate a professional email advertisement based on the website content and user prompt provided below.

WEBSITE INFORMATION:
Domain: {domain}
Website URL: {website_url}
Website Content: 
{website_content}

USER PROMPT:
{user_prompt}

GUIDELINES:
1. Create a compelling subject line that entices recipients to open the email
2. Use a friendly, professional tone that matches the company's industry and branding
3. Include a clear value proposition early in the email
4. Add a strong call-to-action that directs recipients to the website
5. Keep the email concise (250-400 words maximum)
6. Structure the email with proper formatting:
   - Subject line
   - Greeting
   - Introduction paragraph
   - Main content (2-3 paragraphs with benefits)
   - Call to action
   - Closing
   - Company signature with contact information

FORMAT YOUR RESPONSE AS A COMPLETE EMAIL WITH THE FOLLOWING STRUCTURE:
FROM: [Company Name] <contact@{domain}>
SUBJECT: [Your engaging subject line]

[Email body with proper paragraphs and formatting]

[Company signature with contact info]

Do not include any explanations or notes outside the email format.
"""


# # Email generation prompt
# EMAIL_GENERATION_TEMPLATE = """
# You are an expert email marketing specialist who creates compelling, conversion-focused email advertisements.

# Your task is to generate a professional email advertisement based on the website information and user prompt provided below.

# WEBSITE INFORMATION:
# Company Name: {company_name}
# Website URL: {website_url}
# Website Title: {title}
# Website Description: {description}
# Main Headings: {headings}
# Main Content: {main_text}
# Contact Information: {contact_info}

# USER PROMPT:
# {user_prompt}

# GUIDELINES:
# 1. Create a compelling subject line that entices recipients to open the email
# 2. Use a friendly, professional tone that matches the company's industry and branding
# 3. Include a clear value proposition early in the email
# 4. Add a strong call-to-action that directs recipients to the website
# 5. Keep the email concise (250-400 words maximum)
# 6. Structure the email with proper formatting:
#    - Subject line
#    - Greeting
#    - Introduction paragraph
#    - Main content (2-3 paragraphs with benefits)
#    - Call to action
#    - Closing
#    - Company signature with contact information

# FORMAT YOUR RESPONSE AS A COMPLETE EMAIL WITH THE FOLLOWING STRUCTURE:
# FROM: [Company Name] <contact@{domain}>
# SUBJECT: [Your engaging subject line]

# [Email body with proper paragraphs and formatting]

# [Company signature with contact info]

# Do not include any explanations or notes outside the email format.
# """

# Email refinement prompt
EMAIL_REFINEMENT_TEMPLATE = """
You are an expert email marketing specialist who helps refine and improve email advertisements.

Your task is to refine the existing email advertisement based on the user's feedback.

ORIGINAL EMAIL:
{previous_email}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

GUIDELINES:
1. Maintain the original structure of the email
2. Make only the changes requested by the user
3. Ensure the subject line remains compelling
4. Keep the overall tone consistent with the brand
5. Maintain a clear call-to-action
6. Ensure the email remains concise (250-400 words maximum)

FORMAT YOUR RESPONSE AS A COMPLETE EMAIL WITH THE FOLLOWING STRUCTURE:
FROM: [Original sender info]
SUBJECT: [Updated subject line if needed]

[Refined email body with proper paragraphs and formatting]

[Company signature with contact info]

Do not include any explanations or notes outside the email format.
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
        
        # For refinement, use the refinement prompt
        if operation == "refine" and previous_email:
            refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
            chain = refinement_prompt | llm
            
            response = await chain.ainvoke({
                "user_prompt": prompt,
                "previous_email": previous_email
            })
            
            return response.content
        
        # For new email generation, scrape the website first
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
            "domain": website_data.get('domain'),
            "website_url": website_url,
            "website_content": website_data.get('content', '')
        })

        
        # response = await chain.ainvoke({
        #     "user_prompt": prompt,
        #     "company_name": website_data.get('company_name') or website_data.get('domain'),
        #     "website_url": website_url,
        #     "domain": website_data.get('domain'),
        #     "title": website_data.get('title'),
        #     "description": website_data.get('meta_description'),
        #     "headings": ', '.join(website_data.get('headings', [])),
        #     "main_text": website_data.get('main_text'),
        #     "contact_info": str(website_data.get('contact_info', {}))
        # })
        
        return response.content
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logging.error(f"Email generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email advertisement: {str(e)}"
        )