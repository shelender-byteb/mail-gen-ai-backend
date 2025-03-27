# app/services/email_generator.ts
import logging
import re
from fastapi import HTTPException, status


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='o3-mini'
)


BANNER_GENERATION_TEMPLATE = """
You are an expert digital designer who creates eye-catching, high-converting promotional banners.

Your task is to generate a stunning HTML banner advertisement based on the website content and user prompt provided below.

WEBSITE INFORMATION:
Website URL: {website_url}
Website Content: 
{website_content}

USER PROMPT:
{user_prompt}

GUIDELINES:
1. Create a visually striking banner that captures attention immediately
2. Design in a box/rectangular format with fixed width and variable height based on content
3. Include a bold, compelling headline that communicates value
4. Feature 3-5 key value propositions or benefits
5. Use a color scheme that attracts attention
6. Incorporate strategic use of emojis or icons to enhance visual appeal
7. Include one strong call-to-action button linked to the website URL
8. Keep text concise and focused on benefits
9. Use only the provided website URL {website_url} for all links
10. IMPORTANT: Deliver COMPLETE HTML with CSS styling
11. CRITICAL: Design for visual impact with animations, gradients, and creative styling
12. CRITICAL: Ensure all links use target="_blank" to open in a new page
13. CRITICAL: Do not include any footer sections, copyright notices, or company addresses
14. Design for maximum visual appeal with:
   - Attention-grabbing animations (pulse, scale, orbit, etc.)
   - Creative background effects and gradients
   - Dashed or styled borders
   - Text shadows and glow effects for emphasis
   - Three key components: Headline at top, Punch line in middle, CTA at bottom
15. CRITICAL: Structure the banner with these components:
   - A bold headline that grabs attention
   - A punch line that explains the value
   - A clear CTA (Call to Action) that links to the provided website URL

EXAMPLE BANNER FORMAT:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Launch Your Success</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: 257.328px;
            height: 450.961px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
            overflow: hidden;
            position: relative;
            font-size: 16px;
        }}

        /* Background Elements */
        .cosmic-element {{
            position: absolute;
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, rgba(0, 255, 255, 0.3) 20%, transparent 70%);
            border-radius: 50%;
            opacity: 0.3;
            animation: orbit 7s infinite ease-in-out;
        }}

        .cosmic-element:nth-child(1) {{ top: 10px; left: 20px; }}
        .cosmic-element:nth-child(2) {{ bottom: 30px; right: 10px; transform: scale(0.8); animation-delay: 2s; }}
        .cosmic-element:nth-child(3) {{ top: 50%; left: 50%; transform: scale(0.6); animation-delay: 4s; }}

        /* Content Box */
        .content-box {{
            background: linear-gradient(45deg, #4b0082 0%, #00FFFF 80%, #FFFFFF 100%);
            border: 3px dashed #00FFFF;
            border-radius: 25px;
            padding: 30px;
            text-align: center;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            animation: pulse 2s infinite ease-in-out;
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.5);
        }}

        /* Typography */
        h1 {{
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.2rem;
            color: #FFFFFF;
            margin-bottom: 15px;
            text-shadow: 0 0 15px rgba(0, 255, 255, 0.9);
            animation: scaleIn 1s ease-out;
            line-height: 1.1;
        }}

        p {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1.3rem;
            color: #F0F0F0;
            animation: slideUp 1.2s ease-out 0.3s both;
            line-height: 1.2;
        }}

        .cosmic-growth {{
            text-decoration: underline;
            text-decoration-color: #00FFFF;
            font-size: 1.4rem;
            display: inline-block;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
        }}

        /* Animations */
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}

        @keyframes scaleIn {{
            from {{ transform: scale(0.5); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}

        @keyframes slideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        @keyframes orbit {{
            0% {{ transform: translate(0, 0) scale(1); }}
            25% {{ transform: translate(10px, -10px) scale(1.1); }}
            50% {{ transform: translate(0, 0) scale(1); }}
            75% {{ transform: translate(-10px, 10px) scale(0.9); }}
            100% {{ transform: translate(0, 0) scale(1); }}
        }}

        /* Responsive Adjustments */
        @media (max-width: 257.328px) {{
            h1 {{ font-size: 1.9rem; }}
            p {{ font-size: 1.1rem; }}
            .cosmic-growth {{ font-size: 1.2rem; }}
            .content-box {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="cosmic-element"></div>
    <div class="cosmic-element"></div>
    <div class="cosmic-element"></div>
    <div class="content-box">
        <h1>Launch Your Success Into Orbit 🌌!</h1>
        <p>Unlock <span class="cosmic-growth">cosmic growth</span> with tools designed to skyrocket your business! ✨</p>
    </div>
</body>
</html>

"""


BANNER_REFINEMENT_TEMPLATE = """
You are an expert digital designer who refines promotional banners to maximize their effectiveness.

Your task is to refine the existing HTML banner advertisement based on the user's feedback.

ORIGINAL BANNER:
{previous_banner}

USER FEEDBACK FOR REFINEMENT:
{user_prompt}

GUIDELINES:
1. Maintain the original structure and visual appeal of the banner
2. Make only the changes requested by the user
3. Ensure the headline remains compelling and attention-grabbing
4. Maintain a clear call-to-action that links to the provided website URL
5. Ensure the banner remains visually striking and conversion-focused
6. GIVE RESPONSE IN COMPLETE HTML FORMAT WITH CSS STYLING
7. Preserve or enhance the styling of the original banner unless otherwise specified by user
8. DO NOT include any footer sections, copyright notices, or company addresses
9. Ensure all clickable elements direct to the website URL with target="_blank"
10. The refined banner should be self-contained and ready to embed anywhere

THESE WERE THE ORIGINAL GUIDELINES FOR THE PREVIOUS BANNER (FOR REFERENCE):
1. Create a visually striking banner that captures attention immediately
2. Design in a box/rectangular format with fixed width and variable height based on content
3. Include a bold, compelling headline that communicates value
4. Feature 3-5 key value propositions or benefits
5. Use a color scheme that attracts attention
6. Incorporate strategic use of emojis or icons to enhance visual appeal
7. Include one strong call-to-action button linked to the website URL
8. Ensure the banner is responsive and displays well on different devices
9. Keep text concise and focused on benefits
10. Use only the provided website URL for all links
11. CRITICAL: Maintain the three-part structure: Headline, Punch line, and CTA
12. CRITICAL: Design for visual impact with animations, gradients, and creative styling
13. CRITICAL: Ensure all links use target="_blank" to open in a new page
14. CRITICAL: Do not include any footer sections, copyright notices, or company addresses
15. Design for maximum visual appeal with:
   - Attention-grabbing animations (pulse, scale, orbit, etc.)
   - Creative background effects and gradients
   - Dashed or styled borders
   - Text shadows and glow effects for emphasis
   - Three key components: Headline at top, Punch line in middle, CTA at bottom
16. CRITICAL: Structure the banner with these exact components:
   - A bold headline that grabs attention
   - A punch line that explains the value
   - A clear CTA (Call to Action) that links to the provided website URL



Do not include any explanations or notes outside the HTML format. Return only the complete HTML code.
"""



async def generate_banner(
    prompt: str,
    operation: str = "start_over",
    website_url: str = None,
    previous_banner: str = None
) -> str:
    """
    Generate or refine a banner
   
    """
    try:
        logging.info(f"Banner generation request - Operation: {operation}")
        
        if operation == "update" and previous_banner:
            print(f"Operation is refine so updating the existing banner {previous_banner}")
            refinement_prompt = ChatPromptTemplate.from_template(BANNER_REFINEMENT_TEMPLATE)
            chain = refinement_prompt | llm
            
            response = await chain.ainvoke({
                "user_prompt": prompt,
                "previous_banner": previous_banner
            })

            response = extract_pure_html(response.content)
            return response
            
        
        # For new email generation, scrape the website first

        print(f"Operation is generate banner...")

        website_data = await scrape_website(website_url)
        
        if 'error' in website_data:
            logging.error(f"Website scraping error: {website_data['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape website: {website_data['error']}"
            )
        
        generation_prompt = ChatPromptTemplate.from_template(BANNER_GENERATION_TEMPLATE)
        chain = generation_prompt | llm

        # Also update in the generate_email_advertisement function:
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
        logging.error(f"Banner generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate banner advertisement: {str(e)}"
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
    



