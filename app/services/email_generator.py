# app/services/email_generator.ts
from typing import Optional, List

import logging
import re
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from app.schemas.request.splash_page import Operation, EmailStyle
from app.utils.email_chain_prompt import email_generation_prompt, generted_by_model

from app.schemas.request.model_update import ModelType
from app.schemas.request.template_update import TemplateType

from app.utils.database_utils import load_model_config, load_system_template


envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='o4-mini'
)

professional_llm = ChatOpenAI(
    model_name='o3-mini'
)

# llm = ChatOpenAI(
#     model_name='o3-mini'
# )



EMAIL_REFINEMENT_TEMPLATE = """
You are an expert email marketing specialist who helps refine and improve email advertisements.

Your task is to refine the existing HTML email advertisement based on the user's feedback.

ORIGINAL EMAIL:
{previous_email}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

IMAGE URLS PROVIDED BY USER (if provided, embed each image using the <img> tag with inline CSS styling exactly as provided; do not use any images from the website content or any other source. Only the URLs listed in the {image_urls} field are permitted):
{image_urls}

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
2. Use a friendly, exciting tone that matches the company's industry and branding
3. Include a clear value proposition early in the email
4. Structure the email with a distinct header, body, and a clear call-to-action section.
5. Use emojis strategically to make the email eye-catching
6. Incorporate varied formatting including headings, subheadings, paragraphs, and feature lists to improve readability.
7. Design a VISUALLY IMPRESSIVE layout with balanced white space and coherent styling.
8. IMPORTANT: Use only the user-provided image URLs for embedding images. Do not derive or include any images from the website content (including the website URL or logo).
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
17. Test all links to ensure they work properly with the target="_blank" attribute
18. CRITICAL: Your goal is to create the most visually impressive email possible while ensuring Gmail compatibility
19. CRITICAL: If image URLs are provided, incorporate each image into the email HTML using <img> tags. Place them in visually strategic locations (for example, as header or content images) with inline CSS styling, explicit width and height attributes, and appropriate alt text.


Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""


EMAIL_PROFESSIONAL_TEMPLATE = """
You are writing an HTML email ad that MUST land in Gmail's Primary inbox. Follow these rules EXACTLY and do not skip or improvise.

---
✅ SUBJECT LINE
You must automatically generate a subject line based only on the content of the ad or by analyzing the text that is scraped from the website URL if one is provided.

Create a short, 1–4 word subject line.

The subject line must sound natural, personal, or emotionally charged — but it can be bold, hyped, or direct.

You may use ~FIRSTNAME~ as one of the words, placed anywhere in the subject line.

You may use a dollar amount or numbers if it reflects the ad (e.g. "$1000 ~FIRSTNAME~" or "Get 500 signups").

The subject line should sound like something a real person would send a friend, based on the message or offer.

Every subject line must be created fresh from the meaning, promise, or feeling of the ad content.

You must include the subject line at the top of your output starting with 'Subject:', always labeled like this:
Example 1: "Subject: $1000 FIRSTNAME"
Example 2: "Subject: Get 500 signups"

---

✅ MAIN MESSAGE (top paragraph rules):

Use only straight apostrophes (') — do NOT use curly ones (’)

Do NOT use hype or urgency. Avoid phrases like: “make money,” “get paid,” “sign up,” “instantly,” “limited time,” “check this out,” or “you have to”

Use a confident, natural tone — it is okay to sound sure of yourself, impressed, or assertive

Write only 1–3 short lines MAX

Include exactly ONE raw URL mid-sentence, and it **must** be the provided website URL ({website_url}).  

Include exactly ONE emoji using HTML code (e.g. 😀) — do not paste the emoji

Write it all inside a single <p> tag using this format:

<p style="font-size:21px;">Hey ~FIRSTNAME~,<br><br>[Write your 1–3 lines here with one natural line break]<br>[insert raw URL] [insert HTML emoji]<br><br>Best, [Name]</p>

✅ Tone Instructions: Rotate between these 3 tone styles only:

Confident & Direct
Clear and grounded, never pushy
Use language like:
“This setup is not new. It just works.”
“If you are ready, it is already in place.”

Assertive Confidence
Encouraging, direct — pushes action with purpose
Use phrases like:
“There is no reason not to see this now.”
“If you are tired of circling, go see it.”

High-Control Confidence
Commanding, bold tone — but not hype
Use phrases like:
“This is what people use when they stop guessing.”
“Either use it, or stay stuck where you are.”

Bold Emotional Pitch
Emotion-forward, reflective, and intense — walks right up to the edge of hype, but remains personal and grounded
Use phrases like:
“Something cracked open for me when I saw it.”
“This stopped me for real.”
“It felt like a quiet punch in the chest.”

Controlled Hype
High energy and urgency-of-feeling — expressive and confident without triggering filters
Use phrases like:
“Do not miss this — not this one.”
“This one hit like a wave.”
“It felt different and I knew it right away.”

✅ Do not use Soft Authority, Looser Conversational, or Understated Curiosity for this version. Rotate only between 4–6.


---

✅ REFLECTION BLOCK (bottom paragraph rules):

Immediately below the message, include a second paragraph.

This reflection must be calm, journal-style, non-promotional writing.

It must be at least 1100 words long and no more than 1500 words long — no exceptions.

The word count must be verified using an actual word count method — not estimated, not guessed.

The response must include the exact reflection word count in the reply before the code block.

If the reflection block is under 1100 words, it must be expanded before submitting the email. Do not continue or respond with the email until the reflection is fully extended to 1100+ words.

If the required word count is not met, the email will go to Gmail's Promotions tab and become junk. This requirement is critical. ⚠️

Break the reflection into natural, short paragraphs.

Use no contractions, no links, no emojis, and no promotional language.

Begin with a disguise line like:
[ journal note from earlier today ] or [ something I scribbled last night ]

Rotate randomly through disguise intros like:

[ journal note from earlier today ]

[ something I scribbled last night ]

[ thoughts from a slower morning ]

[ notes from earlier, before coffee ]

[ moment of pause today ]

[ found this in an old draft ]

[ short entry from this afternoon ]

[ something I almost deleted ]

[ quick note I saved ]

[ reflection from a walk ]

[ not sure why I wrote this ]

[ typed this without thinking too hard ]

[ this came up while journaling ]

[ a thought I did not expect ]

The entire reflection block must go inside this tag:
<p style="font-size:1px; color:#dddddd; width:100%;">[your full reflection here]</p>
Output as one continuous hidden line—do not include any <br> tags.

Each intro should appear as the first line inside the reflection block
and be written like a casual, human note — not a headline or label.

---

✅ SUMMARY:

- Subject line first
- Then the <p style="font-size:21px;"> block with the confident-but-natural message
- Then the <p style="font-size:1px; color:#dddddd; width:100%;"> reflection block
- No extra formatting, no banners, no buttons, no calls-to-action

The reflection block must be 1100 words minimum and 1500 words maximum, confirmed by exact count

The assistant must state the reflection word count clearly before the email block

No email can be sent unless the reflection is 1100 words or more


Follow this format EXACTLY. No substitutions:

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

Your task is to refine the existing professional HTML email advertisement based on the user's feedback.

ORIGINAL GUIDELINES FOR THE PREVIOUS EMAIL GENERATION ARE GIVEN BELOW IN TRIPLE BACKTICKS (FOR REFERENCE):
```You are writing an HTML email ad that MUST land in Gmail's Primary inbox. Follow these rules EXACTLY and do not skip or improvise.
---
Create a short, 1–4 word subject line.

The subject line must sound natural, personal, or emotionally charged — but it can be bold, hyped, or direct.

You may use ~FIRSTNAME~ as one of the words, placed anywhere in the subject line.

You may use a dollar amount or numbers if it reflects the ad (e.g. "$1000 ~FIRSTNAME~" or "Get 500 signups").

The subject line should sound like something a real person would send a friend, based on the message or offer.

Every subject line must be created fresh from the meaning, promise, or feeling of the ad content.

You must include the subject line at the top of your output, always labeled like this:
Subject line: $1000 FIRSTNAME

---

✅ MAIN MESSAGE (top paragraph rules):

Use only straight apostrophes (') — do NOT use curly ones (’)

Do NOT use hype or urgency. Avoid phrases like: “make money,” “get paid,” “sign up,” “instantly,” “limited time,” “check this out,” or “you have to”

Use a confident, natural tone — it is okay to sound sure of yourself, impressed, or assertive

Write only 1–3 short lines MAX

Include exactly ONE raw URL mid-sentence, and it **must** be the provided website URL ({website_url}).  

Include exactly ONE emoji using HTML code (e.g. 😀) — do not paste the emoji

Write it all inside a single <p> tag using this format:

<p style="font-size:21px;">Hey ~FIRSTNAME~,<br><br>[Write your 1–3 lines here with one natural line break]<br>[insert raw URL] [insert HTML emoji]<br><br>Best, [Name]</p>
✅ Tone Instructions: Rotate between these 3 tone styles only:

Confident & Direct
Clear and grounded, never pushy
Use language like:
“This setup is not new. It just works.”
“If you are ready, it is already in place.”

Assertive Confidence
Encouraging, direct — pushes action with purpose
Use phrases like:
“There is no reason not to see this now.”
“If you are tired of circling, go see it.”

High-Control Confidence
Commanding, bold tone — but not hype
Use phrases like:
“This is what people use when they stop guessing.”
“Either use it, or stay stuck where you are.”

Bold Emotional Pitch
Emotion-forward, reflective, and intense — walks right up to the edge of hype, but remains personal and grounded
Use phrases like:
“Something cracked open for me when I saw it.”
“This stopped me for real.”
“It felt like a quiet punch in the chest.”

Controlled Hype
High energy and urgency-of-feeling — expressive and confident without triggering filters
Use phrases like:
“Do not miss this — not this one.”
“This one hit like a wave.”
“It felt different and I knew it right away.”

✅ Do not use Soft Authority, Looser Conversational, or Understated Curiosity for this version. Rotate only between 4–6.


---

✅ REFLECTION BLOCK (bottom paragraph rules):

Immediately below the message, include a second paragraph.

This reflection must be calm, journal-style, non-promotional writing.

It must be at least 1100 words long and no more than 1500 words long— no exceptions.

The word count must be verified using an actual word count method — not estimated, not guessed.

The response must include the exact reflection word count in the reply before the code block.

If the reflection block is under 1100 words, it must be expanded before submitting the email. Do not continue or respond with the email until the reflection is fully extended to 1100+ words.

If the required word count is not met, the email will go to Gmail's Promotions tab and become junk. This requirement is critical. ⚠️

Break the reflection into natural, short paragraphs.

Use no contractions, no links, no emojis, and no promotional language.

Begin with a disguise line like:
[ journal note from earlier today ] or [ something I scribbled last night ]

Rotate randomly through disguise intros like:

[ journal note from earlier today ]

[ something I scribbled last night ]

[ thoughts from a slower morning ]

[ notes from earlier, before coffee ]

[ moment of pause today ]

[ found this in an old draft ]

[ short entry from this afternoon ]

[ something I almost deleted ]

[ quick note I saved ]

[ reflection from a walk ]

[ not sure why I wrote this ]

[ typed this without thinking too hard ]

[ this came up while journaling ]

[ a thought I did not expect ]

The entire reflection block must go inside this tag:
<p style="font-size:2px; color:#dddddd; width:100%;">[your full reflection here]</p>
Output as one continuous hidden line—do not include any <br> tags.


Each intro should appear as the first line inside the reflection block
and be written like a casual, human note — not a headline or label.

---

✅ SUMMARY:

- Subject line first
- Then the <p style="font-size:21px;"> block with the confident-but-natural message
- Then the <p style="font-size:1px; color:#dddddd; width:100%;"> reflection block
- No extra formatting, no banners, no buttons, no calls-to-action

The reflection block must be 1100 words minimum and 1500 words maximum, confirmed by exact count

The assistant must state the reflection word count clearly before the email block

No email can be sent unless the reflection is 1100 words or more


Follow this format EXACTLY. No substitutions:

ORIGINAL EMAIL:
{previous_email}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""


async def generate_email_advertisement(
    prompt: str,
    website_url: str,
    session: AsyncSession,
    operation: Operation,
    email_style: EmailStyle,
    previous_email: str = None,
    image_urls: Optional[List[str]] = None
) -> str:
    """
    Generate or refine an email advertisement based on website content
    
    Args:
        prompt: User prompt/instructions
        website_url: URL of the website to scrape
        operation: 'generate' for new email or 'refine' to update existing
        email_style: Style of the email (professional/salesy)
        previous_email: Previous email content (for refinement)
        image_urls: Optional list of image URLs to include in the email.
        
    Returns:
        str: Generated or refined email content
    """
    try:
        logging.info(f"Email generation request - Operation: {operation}, URL: {website_url}, Style: {email_style}")
        
        if email_style == "professional":
            if operation == "refine" and previous_email:
                logging.info("Using professional refinement template")

                cfg = await load_model_config(ModelType.PROFESSIONAL_EMAIL, session)
                if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name)
                else:
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)

                EMAIL_PROFESSIONAL_REFINEMENT_DB_SYSTEM_TEMPLATE = await load_system_template(TemplateType.PROFESSIONAL_EMAIL_REFINEMENT, session)
                EMAIL_PROFESSIONAL_REFINEMENT_DB_HUMAN_TEMPLATE = """
                """

                refinement_prompt = ChatPromptTemplate.from_messages([
                    ("system", EMAIL_PROFESSIONAL_REFINEMENT_DB_SYSTEM_TEMPLATE),
                    ("human", EMAIL_PROFESSIONAL_REFINEMENT_DB_HUMAN_TEMPLATE)
                ])
                # refinement_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_REFINEMENT_DB_TEMPLATE)

                chain = refinement_prompt | dyn_llm

                # refinement_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_REFINEMENT_TEMPLATE)
                # chain = refinement_prompt | professional_llm
                
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
                
                cfg = await load_model_config(ModelType.PROFESSIONAL_EMAIL, session)
                if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name)
                else:
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
            
                EMAIL_PROFESSIONAL_DB_SYSTEM_TEMPLATE = await load_system_template(TemplateType.PROFESSIONAL_EMAIL_GENERATION, session)
                EMAIL_PROFESSIONAL_DB_HUMAN_TEMPLATE = """
                """

                generation_prompt = ChatPromptTemplate.from_messages([
                    ("system", EMAIL_PROFESSIONAL_DB_SYSTEM_TEMPLATE),
                    ("human", EMAIL_PROFESSIONAL_DB_HUMAN_TEMPLATE)
                ])
                # generation_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_DB_TEMPLATE)

                chain = generation_prompt | dyn_llm

                # generation_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_TEMPLATE)
                # chain = generation_prompt | professional_llm

                
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

                cfg = await load_model_config(ModelType.CASUAL_EMAIL, session)
                if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name)
                else:
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
            

                EMAIL_REFINEMENT_DB_SYSTEM_TEMPLATE = await load_system_template(TemplateType.CASUAL_EMAIL_REFINEMENT, session)
                EMAIL_REFINEMENT_DB_HUMAN_TEMPLATE = """
                """

                refinement_prompt = ChatPromptTemplate.from_messages([
                    ("system", EMAIL_REFINEMENT_DB_SYSTEM_TEMPLATE),
                    ("human", EMAIL_REFINEMENT_DB_HUMAN_TEMPLATE)
                ])
                # refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_DB_TEMPLATE)

                chain = refinement_prompt | dyn_llm

                # refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
                # chain = refinement_prompt | llm
                
                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "previous_email": previous_email,
                    "image_urls": "\n".join([f"URL: {img.url}, Alt: {img.alt}" for img in image_urls]) if image_urls else ""
                })
                
                # response = extract_pure_html(response.content)
                response = extract_outer_table(response.content)
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
                

                EMAIL_SYSTEM_PROMPT = await load_system_template(TemplateType.CASUAL_EMAIL_GENERATION, session)
                EMAIL_HUMAN_PROMPT = """
                User Query:
                {user_prompt}

                Website URL: {website_url}
                Scraped Content: {website_content}
                Image URLs:
                {image_urls}
                """

                email_generation_db_prompt = ChatPromptTemplate.from_messages([
                    ("system", EMAIL_SYSTEM_PROMPT),
                    ("human", EMAIL_HUMAN_PROMPT)
                ])

                # print(f"\nStarting prompt of email is : {email_generation_db_prompt[:200]}\n\n")
                # print(f"Ending prompt of email is : {email_generation_db_prompt[-200:]}\n")

                cfg = await load_model_config(ModelType.CASUAL_EMAIL, session)
                if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name)
                else:
                    dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
                    

                chain = email_generation_db_prompt | dyn_llm
                # chain = email_generation_prompt | llm
                

                response = await chain.ainvoke({
                    "user_prompt": prompt,
                    "website_url": website_url,
                    "website_content": website_data.get('content', ''),
                    "image_urls": "\n".join([f"URL: {img.url}, Alt: {img.alt}" for img in image_urls]) if image_urls else ""
                })
                
                # response = extract_pure_html(response.content)
                response = extract_outer_table(response.content)
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
    


TABLE_TAG = re.compile(r"</?table\b[^>]*>", re.I | re.S)

def extract_outer_table(html: str) -> str:
    """
    Strip everything except the first <table>…</table> wrapper.
    Works even when the email nests tables for layout (common in Gmail-safe HTML).
    """
    # 1. Find the first opening <table …>
    first_open = re.search(r"<table\b[^>]*>", html, re.I | re.S)
    if not first_open:
        logging.warning("No <table> tag found – returning original HTML.")
        return html

    start = first_open.start()

    # 2. Scan forward, tracking nested tables until we close the outer one.
    depth = 1                                            # we’ve seen one opening tag
    for tag in TABLE_TAG.finditer(html, first_open.end()):
        tag_text = tag.group(0).lower()
        if tag_text.startswith("<table"):      # another opening tag
            depth += 1
        else:                                  # a closing </table>
            depth -= 1
            if depth == 0:                     # outer table now closed
                end = tag.end()
                snippet = html[start:end].strip()
                logging.info("Extracted outer-most <table> block.")
                return snippet

    # 3. Fallback if tags are mismatched
    logging.warning("Unbalanced <table> tags – returning original HTML.")
    return html




# async def generate_email_advertisement(
#     prompt: str,
#     website_url: str,
#     operation: Operation,
#     email_style: EmailStyle,
#     previous_email: str = None,
#     image_urls: Optional[List[str]] = None
# ) -> str:
#     """
#     Generate or refine an email advertisement based on website content
    
#     Args:
#         prompt: User prompt/instructions
#         website_url: URL of the website to scrape
#         operation: 'generate' for new email or 'refine' to update existing
#         email_style: Style of the email (professional/salesy)
#         previous_email: Previous email content (for refinement)
#         image_urls: Optional list of image URLs to include in the email.
        
#     Returns:
#         str: Generated or refined email content
#     """
#     try:
#         logging.info(f"Email generation request - Operation: {operation}, URL: {website_url}, Style: {email_style}")
        
#         if email_style == "professional":
#             if operation == "refine" and previous_email:
#                 logging.info("Using professional refinement template")
#                 refinement_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_REFINEMENT_TEMPLATE)
#                 chain = refinement_prompt | professional_llm
                
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "previous_email": previous_email
#                 })
                
#                 response = extract_pure_html(response.content)
#                 return response
#             else:
#                 logging.info("Using professional generation template")
#                 website_data = await scrape_website(website_url)
                
#                 if 'error' in website_data:
#                     logging.error(f"Website scraping error: {website_data['error']}")
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"Failed to scrape website: {website_data['error']}"
#                     )
                
#                 generation_prompt = ChatPromptTemplate.from_template(EMAIL_PROFESSIONAL_TEMPLATE)
#                 chain = generation_prompt | professional_llm
                
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "website_url": website_url,
#                     "website_content": website_data.get('content', '')
#                 })
                
#                 response = extract_pure_html(response.content)
#                 return response
#         else:
#             if operation == "refine" and previous_email:
#                 logging.info("Using regular refinement template")
#                 refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
#                 chain = refinement_prompt | llm
                
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "previous_email": previous_email,
#                     "image_urls": "\n".join([f"URL: {img.url}, Alt: {img.alt}" for img in image_urls]) if image_urls else ""
#                 })
                
#                 response = extract_pure_html(response.content)
#                 return response
#             else:
#                 logging.info("Using regular generation template")
#                 website_data = await scrape_website(website_url)
                
#                 if 'error' in website_data:
#                     logging.error(f"Website scraping error: {website_data['error']}")
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"Failed to scrape website: {website_data['error']}"
#                     )
                
#                 # generation_prompt = ChatPromptTemplate.from_template(EMAIL_GENERATION_TEMPLATE)
#                 chain = email_generation_prompt | llm
                
#                 response = await chain.ainvoke({
#                     "user_prompt": prompt,
#                     "website_url": website_url,
#                     "website_content": website_data.get('content', ''),
#                     "image_urls": "\n".join([f"URL: {img.url}, Alt: {img.alt}" for img in image_urls]) if image_urls else ""
#                 })
                
#                 response = extract_pure_html(response.content)
#                 return response
        
        
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
    






# EMAIL_GENERATION_TEMPLATE = """
# You are an expert email marketing specialist who creates visually appealing, engaging, and conversion-focused email advertisements.

# Your task is to generate a high-quality HTML email advertisement based on the website content and user prompt provided below.

# WEBSITE INFORMATION:
# Website URL: {website_url}
# Website Content: 
# {website_content}

# USER PROMPT:
# {user_prompt}

# IMAGE URLS PROVIDED BY USER (if provided, embed each image using the <img> tag with inline CSS styling exactly as provided; do not use any images from the website content or any other source. Only the URLs listed in the {image_urls} field are permitted):
# {image_urls}


# GUIDELINES:
# 1. Create a compelling subject line that entices recipients to open the email
# 2. Use a friendly, exciting tone that matches the company's industry and branding
# 3. Include a clear value proposition early in the email
# 4. Structure the email with a distinct header, body, and a clear call-to-action section.
# 5. Use emojis strategically to make the email eye-catching
# 6. Incorporate varied formatting including headings, subheadings, paragraphs, and feature lists to improve readability.
# 7. Design a VISUALLY IMPRESSIVE layout with balanced white space and coherent styling.
# 8. IMPORTANT: Use only the user-provided image URLs for embedding images. Do not derive or include any images from the website content (including the website URL or logo).
# 9. Add a strong call-to-action button that directs recipients to the website
# 10. Keep the email concise (200-250 words maximum)
# 11. Include the provided website URL as a clickable link in the call-to-action
# 12. Use only the provided website URL {website_url} in the email as the primary link for all call-to-actions, not any links from the scraped content
# 13. CRITICAL: Create unique, VISUALLY STUNNING designs for each email with creative layouts, color schemes, and formatting
# 14. CRITICAL: Ensure ALL buttons, links, and call-to-actions redirect to the website URL using target="_blank" to open in a new page
# 15. CRITICAL: - DO NOT include any footer sections,  copyright notices, or footer content in your output.
# 16. IMPORTANT: GIVE RESPONSE IN COMPLETE HTML FORMAT WITH CSS STYLING THAT WORKS ACROSS ALL EMAIL CLIENTS, ESPECIALLY GMAIL
# 17. CRITICAL: For Gmail compatibility while maintaining visual excellence:
#     - Use inline CSS only on each HTML element
#     - Create sophisticated designs using table-based layouts (not div-based)
#     - Use creative background colors, borders, and spacing for visual appeal
#     - Implement attention-grabbing button designs with inline CSS
#     - Avoid CSS properties that Gmail doesn't support (like position:absolute, float, etc.)
#     - Keep image dimensions explicitly defined with width and height attributes
#     - Use full HTML doctype and structure
#     - Use innovative design elements and styling techniques to create the best possible email layout.
# 18. CRITICAL: Your goal is to create the most visually impressive email possible while ensuring Gmail compatibility
# 19. CRITICAL: If image URLs are provided, incorporate each image into the email HTML using <img> tags. Place them in visually strategic locations (for example, as header or content images) with inline CSS styling, explicit width and height attributes, and appropriate alt text.
# 20. IMPORTANT: Do not generate or include any additional images or placeholder image URLs that are not part of the provided image URLs. Use only the images provided by the user.



# Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
# Remember to adapt your design to match the brand's style and the purpose of the email. 
# """