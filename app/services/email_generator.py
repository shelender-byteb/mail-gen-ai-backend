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
    - No Salutation
    - Introduction paragraph
    - Main content (2-3 paragraphs with benefits)
    - Call to action
    - Closing
    7. DO NOT include any headers, footers, or salutations (no "Dear" or "Hello" openings, no signature at the end)
    8. Include provided website URL {website_url} as contact details in the end
    9. Use only the provided website URL {website_url} in the email as the primary link for all call-to-actions, not any links from the scraped content

    FORMAT YOUR RESPONSE AS A COMPLETE EMAIL WITH THE FOLLOWING STRUCTURE:
    FROM: [Company Name]
    SUBJECT: [Your engaging subject line]

    [Email body with proper paragraphs and formatting]

    [Company signature with contact info]

    EXAMPLES OF SUCCESSFUL EMAILS:

    Email 1:
    Hello There,
    We live in historic times worldwide. Make 2025 historic for you, as you have the power to do so!
    This one has a special Promo Code - Gamma40
    You need to sign up under me to get the max for that
    https://superhotopp.com/lunerhive
    A New program has opened that you'll love, called Super Hot Opp (ortunity)
    The Admins are giving away their signups to members, into the 1000's of them
    Make residual and lump sums in cash - up to 98 dollars a lump!
    Even if the signup was sent to you by the admins...
    Is that free money? YES Yes yes...
    ► Get your programs out there with SOME STYLE
    Also get 2 free hours of advertising when you join today
    Also get 12 special effects on your ads - never seen before + 1 of a kind effects!
    Super simple, just add in your ads.
    Show your smart ad rotator and get even more time on your ads - EASY and CLEAR to do.
    And if you want more???
    The upgrades are only 3.99← Value packed and super low!
    Get the Super Hot Opp Here

    Email 2:
    Hello My Fellow Marketer,
    Have you ever wished for a Money Tree
    where you could just shake it and money
    would fall down?<contact@{domain}>
    I found one and you can have one too!
    This is the cheapest, simplest and fastest
    way I have ever seen to get money. PERIOD.
    Take a look at my Money Tree and Get Ya One!
    - Richard Daigle

    Email 3:
    "USE OUR DONE 4 YOU"..."SUPER POWERFUL LANDING PAGES TO PROMOTE YOUR GREAT BUSINESS PLUS GET PAID"$$$..
    Struggling To Stand Out?..Are Your Landing Pages Being Ignored?''
    We Have The Low Cost Answer...
    YES Use Our Super Powerful Landing Pages To Promote Your Great Programs!!!..
    One Time Low Cost USE Them FOREVER.!!!...
    JOIN NOW CLICK HERE... https://tinyurl.com/ytw3a6kb
    PAY With PayPal 1707nashville@gmail.com
    CashApp $robert476
    Zelle (929)-531 2834
    JOIN NOW START GETTING PAID SUPER FAST.$$$....
    YES GET CASH-FLOW NOW.!!!..
    ALL THE BEST...

    Email 4:
    herculist Do The Math! $900 A Day-Keep 100%-No Monthly Fees
    Say goodbye to rush hour traffic, the 9-5 grind, trading time for money or not making enough money online! Our proven and easy to follow program makes earning $900/day, with zero monthly fees, more than possible. Free Blueprint- Click Here
    This lifestyle changing opportunity supported by a 50k plus community of like-minded, work from home members, makes it easy to succeed from anywhere WIFI is available. https://www.make900dailyonlinefast.com/ready
    WORLDWIDE CASH COWS

    Email 5:
    ★ (You Found it) - The One-Page Funnel 3.0
    Easy Passive Income with DFY funnel
    100% Done-For-You funnel – No setup needed!
    Automated sales system – Closes sales for you.
    Built-in follow-up – Promotes multiple offers on autopilot!
    No auto-responder needed.
    Every lead is hard coded to YOU for life.
    Instant Traffic Solution – Just plug & play!
    Click Below To Get Access To this amazing program.
    Also, get Access to these Amazing Bonuses:
    1. Facebook group to learn Social media strategies.
    2. DM Scripts, MRR products and Free Premium E-books.
    3. Free Traffic Rotator with up to 5000 clicks from Safelists.
    https://itsylinx.com/NOTECHSKILLS
    You get all this for $7.
    To Your Success,
    Richard Moore

    Do not include any explanations or notes outside the email format.
"""


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
            print(f"Operation is refine so updating the existing email {previous_email[:100]}")
            refinement_prompt = ChatPromptTemplate.from_template(EMAIL_REFINEMENT_TEMPLATE)
            chain = refinement_prompt | llm
            
            response = await chain.ainvoke({
                "user_prompt": prompt,
                "previous_email": previous_email
            })
            
            return response.content
        
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