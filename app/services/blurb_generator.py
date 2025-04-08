import logging
import re

from fastapi import HTTPException, status

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from app.schemas.request.blurb_requests import Operation

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='o3-mini'
)

# Text Emphasis: Underline 'cosmic growth' with CSS (text-decoration), matching the underline color to a key accent in the design. Use larger font sizes (e.g., headline: 1.8rem–2.5rem, subheading: 1rem–1.5rem) to dominate the space, with 'cosmic growth' optionally enlarged further.

POWERBLURB_GENERATION_TEMPLATE = """
Create a complete HTML code for a visually stunning splash page ad that fits precisely within a 257.328-pixel wide by 450.961-pixel high panel, featuring a bold headline and an engaging subheading, optimized for visual impact.
WEBSITE INFORMATION:
Website URL: {website_url}
Website Content: 
{website_content}

USER PROMPT:
{user_prompt}


Based on the above, generate a bold headline and an engaging subheading.
Include all styling within a <style> tag in the HTML <head> using CSS to achieve the design. Do not include a CTA button or link; instead, enlarge and emphasize the text to fill the content area. Follow these guidelines to ensure each version is unique and creative:

Core Requirements:
Size: Set the body to exactly 257.328px wide and 450.961px high, with the content box filling the full dimensions (width: 100%; height: 100%) using display: flex to center text vertically and horizontally. Use padding (e.g., 20px–30px) for whitespace.
Background: Keep the body background transparent, applying all color and visual effects within the .content-box using a unique gradient each time.
Responsiveness: Include a @media query for max-width: 257.328px to slightly scale down text and padding if needed, ensuring consistency within the fixed size.

Unique Variations (Randomize These Each Time):
Color Scheme: Use a purple-dominant gradient as a base (e.g., #1a0033, #4b0082, #800080), mixed with one or two contrasting colors (e.g., cyan #00FFFF, teal #008080, gold #FFD700, magenta #FF00FF, white #FFFFFF) for the .content-box background. Vary the gradient direction (e.g., 45deg, 180deg, 270deg) and stops (e.g., 0%, 50%, 100%). Define accent colors for text shadows, borders, and underlines.
Typography: Pair a unique, eye-catching font for the headline (e.g., 'Orbitron', 'Russo One', 'Playfair Display', 'Futura', 'Bebas Neue') with a contrasting, readable font for the subheading (e.g., 'Space Mono', 'Roboto', 'Open Sans', 'Montserrat'). Import fonts from Google Fonts via @import. Adjust font sizes, weights, and shadows (e.g., text-shadow) for diversity.
Background Elements: Add 1–3 dynamic shapes (e.g., stars, circles, polygons, waves) as <div>s with classes like .cosmic-element. Style with CSS properties (e.g., radial-gradient, border-radius, opacity: 0.2–0.4) and position absolutely (e.g., top, left, bottom, right). Vary their size (100px–200px) and placement each time.
Animations: Apply distinct @keyframes animations to:
- .content-box (e.g., slide-in from top/bottom, zoom-in, pulse, rotate slightly).
- Headline (e.g., bounce, fade, typewriter effect, scale).
- Subheading (e.g., fade-in with delay, slide-up, glow).
- Background elements (e.g., spin, float, twinkle, orbit) with unique durations (e.g., 5s–12s) and easing (e.g., linear, ease-in-out).
Content Box Styling: Vary the border (e.g., 1px–3px, solid/dashed, #FFFFFF or accent color), border-radius (e.g., 10px–25px), and box-shadow (e.g., glow, soft, bold with accent color). Experiment with opacity or layered gradients for depth.

Creative Guidelines:
Cosmic Themes: Each version should evoke a distinct cosmic vibe (e.g., galaxy clusters, supernova burst, starry void, nebula mist, sci-fi portal). Avoid repeating themes or styles from previous versions.
Minimalism: Keep the design clean with ample whitespace within the gradient-filled box, ensuring a professional yet bold look.
Uniqueness: Randomize color palettes, font pairings, shape types, animation styles, and box effects to create a fresh identity each time. For example:
- One version might use a teal-to-purple gradient with spinning polygons and a pulsing box.
- Another could feature a magenta-to-gold gradient with twinkling stars and a sliding headline.
Diversity Requirement (CRITICAL): For each design element (e.g., color scheme, typography, layout, background elements, animations), randomly select one option from a provided list. Even without previous output history, each output must be generated using independent random choices to ensure a fresh and varied design every time.

Emojis: Include 🌌 and ✨ in the HTML as specified, ensuring they integrate naturally with the text.

CRITICAL: The generated HTML must strictly use a body width of 257.328px and a height of 450.961px—no adjustments or responsive changes are allowed.
CRITICAL: **Incorporate Website Context**
    - Use the provided website URL and scraped content to:
    - Reflect relevant branding, themes, or content from the website.
    - Integrate significant cues, or textual details from the scraped content.
    - Ensure that the splash page resonates with the website’s overall identity.



EXAMPLE SPLASH PAGE AD:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cosmic Splash Ad</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Montserrat:wght@400&display=swap');
 
    html, body {{
      margin: 0;
      padding: 0;
      width: 257.328px;
      height: 450.961px;
      background: transparent;
    }}
 
    body {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}
 
    .content-box {{
      width: 100%;
      height: 100%;
      padding: 25px;
      box-sizing: border-box;
      background: linear-gradient(135deg, #FF00FF 0%, #008080 100%);
      border: 2px solid #FFFFFF;
      border-radius: 20px;
      box-shadow: 0 0 20px #FF00FF;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      position: relative;
      animation: zoomIn 1.5s ease-out;
    }}
 
    h1 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 2.2rem;
      color: #FFFFFF;
      margin: 0;
      text-align: center;
      text-shadow: 0 0 6px #FFD700;
      animation: bounceIn 1s ease-out;
    }}
 
    p {{
      font-family: 'Montserrat', sans-serif;
      font-size: 1.3rem;
      color: #FFFFFF;
      margin-top: 20px;
      text-align: center;
      text-shadow: 0 0 4px #00FFFF;
      animation: fadeUp 1.8s ease-in-out;
    }}
 
    .underline {{
      text-decoration: underline;
      text-decoration-color: #FFD700;
      font-weight: bold;
    }}
 
    .cosmic-element {{
      position: absolute;
      border-radius: 50%;
      opacity: 0.3;
      background: radial-gradient(circle, #FFFFFF 0%, #FF00FF 100%);
      animation: float 10s infinite ease-in-out;
    }}
 
    .circle1 {{
      width: 140px;
      height: 140px;
      top: -30px;
      left: -30px;
      animation-delay: 0s;
    }}
 
    .circle2 {{
      width: 120px;
      height: 120px;
      bottom: -20px;
      right: -20px;
      animation-delay: 3s;
    }}
 
    .circle3 {{
      width: 100px;
      height: 100px;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation: twinkle 8s infinite linear;
    }}
 
    @keyframes zoomIn {{
      0% {{ transform: scale(0.8); opacity: 0; }}
      100% {{ transform: scale(1); opacity: 1; }}
    }}
 
    @keyframes bounceIn {{
      0% {{ transform: translateY(-50px); opacity: 0; }}
      60% {{ transform: translateY(10px); opacity: 1; }}
      100% {{ transform: translateY(0); }}
    }}
 
    @keyframes fadeUp {{
      0% {{ transform: translateY(30px); opacity: 0; }}
      100% {{ transform: translateY(0); opacity: 1; }}
    }}
 
    @keyframes float {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-15px); }}
    }}
 
    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.3; }}
      50% {{ opacity: 0.6; }}
    }}
 
    @media (max-width: 257.328px) {{
      .content-box {{
        padding: 18px;
      }}
      h1 {{
        font-size: 1.9rem;
      }}
      p {{
        font-size: 1.1rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="content-box">
    <div class="cosmic-element circle1"></div>
    <div class="cosmic-element circle2"></div>
    <div class="cosmic-element circle3"></div>
    <h1>Launch Your Success Into Orbit 🌌!</h1>
    <p>Unlock <span class="underline">cosmic growth</span> with tools designed to skyrocket your business! ✨</p>
  </div>
</body>
</html>

Provide the full HTML code, including the <style> tag with all CSS, ready to run as a standalone page. Push the boundaries of creativity while staying true to the cosmic, text-focused aesthetic, ensuring every version feels vibrant, unique, and visually engaging within the small panel.
"""


POWERBLURB_REFINEMENT_TEMPLATE = """
You are an expert digital designer who refines Hercu/PowerBlurbs to enhance visual impact and creativity.

Your task is to refine the existing HTML splash page ad based on the user's feedback in triple backticks.

ORIGINAL POWERBLURB:
{previous_blurb}

USER FEEDBACK FOR REFINEMENT:
```{user_prompt}```

Please apply the following guidelines, ensuring the final design remains within a 257.328-pixel wide by 450.961-pixel high panel and retains the cosmic, text-focused aesthetic described previously.

THESE WERE THE ORIGINAL GUIDELINES FOR THE BLURB GENERATION (FOR REFERENCE):
Include all styling within a <style> tag in the HTML <head> using CSS to achieve the design. Do not include a CTA button or link; instead, enlarge and emphasize the text to fill the content area. Follow these guidelines to ensure each version is unique and creative:

Core Requirements:
Size: Set the body to exactly 257.328px wide and 450.961px high, with the content box filling the full dimensions (width: 100%; height: 100%) using display: flex to center text vertically and horizontally. Use padding (e.g., 20px–30px) for whitespace.
Background: Keep the body background transparent, applying all color and visual effects within the .content-box using a unique gradient each time.
Responsiveness: Include a @media query for max-width: 257.328px to slightly scale down text and padding if needed, ensuring consistency within the fixed size.

Unique Variations (Randomize These Each Time):
Color Scheme: Use a purple-dominant gradient as a base (e.g., #1a0033, #4b0082, #800080), mixed with one or two contrasting colors (e.g., cyan #00FFFF, teal #008080, gold #FFD700, magenta #FF00FF, white #FFFFFF) for the .content-box background. Vary the gradient direction (e.g., 45deg, 180deg, 270deg) and stops (e.g., 0%, 50%, 100%). Define accent colors for text shadows, borders, and underlines.
Typography: Pair a unique, eye-catching font for the headline (e.g., 'Orbitron', 'Russo One', 'Playfair Display', 'Futura', 'Bebas Neue') with a contrasting, readable font for the subheading (e.g., 'Space Mono', 'Roboto', 'Open Sans', 'Montserrat'). Import fonts from Google Fonts via @import. Adjust font sizes, weights, and shadows (e.g., text-shadow) for diversity.
Background Elements: Add 1–3 dynamic shapes (e.g., stars, circles, polygons, waves) as <div>s with classes like .cosmic-element. Style with CSS properties (e.g., radial-gradient, border-radius, opacity: 0.2–0.4) and position absolutely (e.g., top, left, bottom, right). Vary their size (100px–200px) and placement each time.
Animations: Apply distinct @keyframes animations to:
- .content-box (e.g., slide-in from top/bottom, zoom-in, pulse, rotate slightly).
- Headline (e.g., bounce, fade, typewriter effect, scale).
- Subheading (e.g., fade-in with delay, slide-up, glow).
- Background elements (e.g., spin, float, twinkle, orbit) with unique durations (e.g., 5s–12s) and easing (e.g., linear, ease-in-out).
Content Box Styling: Vary the border (e.g., 1px–3px, solid/dashed, #FFFFFF or accent color), border-radius (e.g., 10px–25px), and box-shadow (e.g., glow, soft, bold with accent color). Experiment with opacity or layered gradients for depth.

Creative Guidelines:
Cosmic Themes: Each version should evoke a distinct cosmic vibe (e.g., galaxy clusters, supernova burst, starry void, nebula mist, sci-fi portal). Avoid repeating themes or styles from previous versions.
Minimalism: Keep the design clean with ample whitespace within the gradient-filled box, ensuring a professional yet bold look.
Uniqueness: Randomize color palettes, font pairings, shape types, animation styles, and box effects to create a fresh identity each time. For example:
- One version might use a teal-to-purple gradient with spinning polygons and a pulsing box.
- Another could feature a magenta-to-gold gradient with twinkling stars and a sliding headline.
Diversity Requirement (CRITICAL): For each design element (e.g., color scheme, typography, layout, background elements, animations), randomly select one option from a provided list. Even without previous output history, each output must be generated using independent random choices to ensure a fresh and varied design every time.

Emojis: Include 🌌 and ✨ in the HTML as specified, ensuring they integrate naturally with the text.

CRITICAL: The generated HTML must strictly use a body width of 257.328px and a height of 450.961px—no adjustments or responsive changes are allowed.

Provide the complete HTML code, including a <style> tag with all CSS, ready to run as a standalone page. Do not include any explanations or notes outside the HTML code.
"""


async def generate_power_blurb(
    prompt: str,
    website_url: str,
    operation: Operation,
    previous_blurb: str = None
) -> str:
    """
    Generate or refine a PowerBlurb advertisement based on website content.
    """
    try:
        logging.info(f"PowerBlurb generation request - Operation: {operation}, URL: {website_url}")
        
        if operation == "update" and previous_blurb:
            print(f"Operation is update so updating the existing blurb {previous_blurb}")
            refinement_prompt = ChatPromptTemplate.from_template(POWERBLURB_REFINEMENT_TEMPLATE)
            chain = refinement_prompt | llm
            
            response = await chain.ainvoke({
                "user_prompt": prompt,
                "previous_blurb": previous_blurb
            })

            response = extract_pure_html(response.content)
            return response
            
        print("Operation is generate...")
        website_data = await scrape_website(website_url)
        
        if 'error' in website_data:
            logging.error(f"Website scraping error: {website_data['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape website: {website_data['error']}"
            )
        
        generation_prompt = ChatPromptTemplate.from_template(POWERBLURB_GENERATION_TEMPLATE)
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
        logging.error(f"PowerBlurb generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PowerBlurb advertisement: {str(e)}"
        )

def extract_pure_html(response_content: str) -> str:
    """
    Extract pure HTML content from the response.
    """
    html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', response_content, re.DOTALL | re.IGNORECASE)
    if html_match:
        logging.info("Extracted pure HTML")
        return html_match.group(1)
    else:
        logging.warning(f"Could not extract pure HTML. Full response: {response_content}")
        return response_content
