import logging
import re

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from app.schemas.request.blurb_requests import Operation

from app.utils.database_utils import load_model_config, load_system_template, get_llm

from app.schemas.request.model_update import ModelType
from app.schemas.request.template_update import TemplateType

envs = get_envs_setting()

llm = ChatOpenAI(
    model_name='o3-mini'
)


import random, secrets

# --- 1. random palettes, fonts, etc. ---------------------------

GRADIENTS = [
    ("135deg", "#4B0082", "#00FFFF"),
    ("45deg",  "#1a0033", "#FFD700"),
    ("180deg", "#32004b", "#FF00FF"),
    ("120deg", "#2e004f", "#008080"),
    ("45deg",  "#ff512f", "#dd2476"),
    ("120deg", "#00c6ff", "#0072ff"),
    ("180deg", "#834d9b", "#d04ed6"),
    ("300deg", "#ee0979", "#ff6a00"),
    ("240deg", "#00d2ff", "#928dab"),
    ("30deg",  "#3a1c71", "#d76d77"),
    ("150deg", "#0099F7", "#F11712")
]

# 🔠 HEADLINE FONTS — removed extra‑bulky/all‑caps sets
HEADLINE_FONTS = [
    "Georgia,serif",
    "Gill Sans,Gill Sans MT,Calibri,sans-serif",
    "Lucida Sans,Liberation Sans,Verdana,sans-serif",
    "Tahoma,Geneva,sans-serif",
    "Trebuchet MS,Helvetica,sans-serif"
]

# 🔠 SUB FONTS — kept all; none are oversize for 1.2‑1.4 rem.
SUB_FONTS = [
    "Verdana,Geneva,sans-serif",
    "Trebuchet MS,Helvetica,sans-serif",
    "Courier New,Courier,monospace",
    "Georgia,serif",
    "Roboto,Arial,Helvetica,sans-serif",
    "Helvetica,Arial,sans-serif",
    "Calibri,Candara,Segoe UI,Optima,sans-serif",
    "Lucida Sans Unicode,Lucida Grande,sans-serif",
    "Gill Sans,Gill Sans MT,sans-serif",
    "Times New Roman,Times,serif"
]

ANIM_PRESETS = [
    "bounceIn",
    "scaleUp",
    "rotatePop",
    "fadeSlide",
    "flipIn",
    "slideUp",
    "zoomRotate",
    "pulseGlow",
    "swingDrop",
    "elasticPop"
]


# Text Emphasis: Underline 'cosmic growth' with CSS (text-decoration), matching the underline color to a key accent in the design. Use larger font sizes (e.g., headline: 1.8rem–2.5rem, subheading: 1rem–1.5rem) to dominate the space, with 'cosmic growth' optionally enlarged further.


POWERBLURB_GENERATION_TEMPLATE = """
Create a HTML code for a visually stunning powerblurb ad that fits precisely within a 257.328-pixel wide by 450.961-pixel high panel, featuring a bold headline and an engaging subheading, optimized for visual impact.

✦✦ POWERBLURB INLINE-ONLY SPEC ✦✦
(Use exactly; no extra tags outside <div>)

— WHAT TO BUILD —
• Produce ONE self-contained <div id="blurb"> snippet sized **257.328 px × 450.961 px**.
• NO <!doctype>, <html>, <head>, <body>, <style>, <link>, or @import tags.
• ALL styling must be inline (style="…") on each element.
• Implement headline + subheading plus optional background shapes.
• Use emojis like 🌌 and ✨ naturally inside the text.

— ANIMATION —
• Do NOT use CSS @keyframes.
• Instead, add a <script> tag as the last child of the root <div> and animate with the Web Animations API (element.animate[…]).
• Keep JS short and self-contained; do not reference external files.

— TYPOGRAPHY —
• Do NOT use @import or @font-face.
• If a display font is desired, list it first and fall back to web-safe fonts, e.g. font-family:'Orbitron',sans-serif.
  (Assume the host page may already load that font; otherwise the fallback shows.)

— LAYOUT RULES —
• Root <div> style **must include**:
  width:257.328px; height:450.961px; padding (20-30px); display:flex; flex-direction:column; justify-content:center; align-items:center; position:relative.
• Background: linear-gradient with a purple base + 1-2 contrasting colours (random each time).
• Text shadows, borders, underline colour, etc. also inline.
• Do **not** insert any CTA links or buttons.

— VARIATION REQUIREMENT —
Randomly choose (independently each run):
• Gradient angles and colours
• Font pair (headline vs subheading)
• Border style/radius, shadow strength
• 0–3 decorative “cosmic-element” <div>s (each positioned abs.; size 100-200 px; low opacity)
• Animation presets (e.g. bounce, scale, fade, rotate) realised via JS.


CRITICAL: The generated HTML must strictly use a body width of 257.328px and a height of 450.961px—no adjustments or responsive changes are allowed.
CRITICAL: **Incorporate Website Context**
    - Use the provided website URL and scraped content to:
    - Reflect relevant branding, themes, or content from the website.
    - Integrate significant cues, or textual details from the scraped content.
    - Ensure that the splash page resonates with the website’s overall identity.


–– PLACEHOLDER VALUES (supplied in each query at runtime by user) ––
{user_prompt}        – the user’s creative brief  
{website_url}        – source URL for brand context  
{website_content}    – text scraped from that URL

–– DESIGN SEED (Supplied in each query at runtime by user. Use exactly as given, do not invent) ––
GRADIENT:         {gradient}
HEADLINE_FONT:    {headline_font}
SUB_FONT:         {sub_font}
ANIMATION_PRESET: {anim}
BORDER_RADIUS:    {border_radius}px
BORDER_PX:        {border_px}px
BORDER_STYLE:     {border_style}
SHADOW:           {shadow_strength}px
SEED_ID:          {seed_id}

— OUTPUT FORMAT —
Return **only** the root <div> with its children and the inline <script>. No explanations, no comments outside the code.


--- **Appeal & Variety Self-Check**: Before returning HTML, auto-verify that a fresh color palette (extracted from website content or a new complementary trio) is applied and at least two creative elements—gradient angle, border treatment, font pairing, or emoji/icon accents—differ from defaults, guaranteeing each banner looks new and striking; re-generate until this test passes.

EXAMPLE SPLASH PAGE AD:
<div id="blurb" style="width:257.328px;height:450.961px;padding:25px;box-sizing:border-box;background:linear-gradient(135deg,#FF00FF 0%,#008080 100%);border:2px solid #FFFFFF;border-radius:20px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;">
  <h1 id="headline" style="font-family:Arial,Helvetica,sans-serif;font-size:2.2rem;color:#FFFFFF;margin:0;text-align:center;text-shadow:0 0 6px #FFD700;">
    Launch Your Success Into Orbit 🌌!
  </h1>

  <p id="sub" style="font-family:Verdana,Geneva,sans-serif;font-size:1.3rem;color:#FFFFFF;margin-top:20px;text-align:center;text-shadow:0 0 4px #00FFFF;">
    Unlock <span style="text-decoration:underline;text-decoration-color:#FFD700;font-weight:bold;">cosmic growth</span> with tools designed to skyrocket your business! ✨
  </p>

  <script>
    /* === JS animations replacing CSS @keyframes === */
    (function () {{
      const headline = document.getElementById('headline');
      const sub      = document.getElementById('sub');

      /* bounce-in headline */
      headline.animate([
        {{ transform:'translateY(-50px)', opacity:0   }},
        {{ transform:'translateY(10px)',  opacity:1, offset:0.60 }},
        {{ transform:'translateY(0)',     opacity:1   }}
      ], {{ duration:1000, easing:'ease-out' }});

      /* fade-up subheading */
      sub.animate([
        {{ transform:'translateY(30px)', opacity:0 }},
        {{ transform:'translateY(0)',    opacity:1 }}
      ], {{ duration:1800, easing:'ease-in-out' }});

      /* optional floating background dots if any exist */
      document.querySelectorAll('.cosmic-element').forEach(el => {{
        el.animate(
          [{{ transform:'translateY(0)' }},
           {{ transform:'translateY(-15px)' }},
           {{ transform:'translateY(0)' }}], 
          {{ duration:10000, easing:'ease-in-out', iterations:Infinity }}
        );
      }});
    }})();
  </script>
</div>
"""

POWERBLURB_REFINEMENT_TEMPLATE = """
You are an elite digital designer who **refines** PowerBlurbs.  
Your job: adjust the existing snippet exactly to the user’s feedback while keeping all
inline-only constraints.

✦✦ INLINE-ONLY SPEC (MUST follow) ✦✦
• The finished code must be **one self-contained** `<div id="blurb"> … </div>` snippet.  
• **No** `<!doctype>`, `<html>`, `<head>`, `<body>`, `<style>`, `<link>`, `@import`, or `@keyframes`.  
• All CSS inline via `style="…"`.  
• Width **257.328 px** & height **450.961 px** fixed; keep `display:flex` centering.  
• Use only web-safe fonts (e.g. Arial, Helvetica, Verdana, Georgia, Courier).  
• Animations must be in an inline `<script>` and use the Web Animations API (`element.animate`).  
• May include 0-3 `.cosmic-element` shapes, headline `<h1>`, subheading `<p>`, emojis 🌌 ✨.  
• Do **not** add CTA buttons or links.

When refining:
1. Keep the cosmic, text-focused aesthetic.
2. Respect every size / inline rule above.
3. Apply the feedback **precisely** (e.g., colour tweak, new copy, font change, extra shape).
4. If you change colours, fonts, or animation, do so inline and mention none of the old code.
5. Preserve any unique IDs or JS seed comments unless the feedback asks otherwise.

Return **only** the updated `<div id="blurb"> … </div>` with its children and inline `<script>`.  
NO explanations or extra text.

You will be given the following details in each query:
- **Original Blurb HTML to edit:** {previous_blurb}
- **User Feedback / change requests:** {user_prompt}


"""



async def generate_power_blurb(
    prompt: str,
    session: AsyncSession,
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
            # refinement_prompt = ChatPromptTemplate.from_template(POWERBLURB_REFINEMENT_TEMPLATE)
            # chain = refinement_prompt | llm
            cfg = await load_model_config(ModelType.BLURB, session)
            # if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
            #     dyn_llm = ChatOpenAI(model_name=cfg.model_name)
            # else:
            #     dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
            dyn_llm = get_llm(cfg.provider, cfg.model_name, cfg.temperature)

            BLURB_REFINEMENT_DB_SYSTEM_TEMPLATE = await load_system_template(TemplateType.BLURB_REFINEMENT, session)
            BLURB_REFINEMENT_HUMAN = """
            ORIGINAL BLURB (edit this, do not discard):
            {previous_blurb}

            USER FEEDBACK:
            {user_prompt}
            """

            refinement_prompt = ChatPromptTemplate.from_messages([
                ("system", BLURB_REFINEMENT_DB_SYSTEM_TEMPLATE),
                ("human",  BLURB_REFINEMENT_HUMAN),
            ])

            # refinement_prompt = ChatPromptTemplate.from_template(BLURB_REFINEMENT_DB_TEMPLATE)

            chain = refinement_prompt | dyn_llm
            
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
        
        cfg = await load_model_config(ModelType.BLURB, session)
        # if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
        #     dyn_llm = ChatOpenAI(model_name=cfg.model_name)
        # else:
        #     dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
        dyn_llm = get_llm(cfg.provider, cfg.model_name, cfg.temperature)

        BLURB_GENERATION_DB_SYSTEM_TEMPLATE = await load_system_template(TemplateType.BLURB_GENERATION, session)
        BLURB_GENERATION_HUMAN_TEMPLATE = """
        User Query:
        {user_prompt}

        Website URL: {website_url}
        Scraped Content: {website_content}

        GRADIENT: {gradient}
        HEADLINE_FONT: {headline_font}
        SUB_FONT: {sub_font}
        ANIM: {anim}
        BORDER_RADIUS: {border_radius}px
        BORDER_PX: {border_px}px
        BORDER_STYLE: {border_style}
        SHADOW: {shadow_strength}px
        SEED_ID: {seed_id}
        """

        generation_prompt = ChatPromptTemplate.from_messages([
            ("system", BLURB_GENERATION_DB_SYSTEM_TEMPLATE),
            ("human",  BLURB_GENERATION_HUMAN_TEMPLATE),
        ])
        # generation_prompt = ChatPromptTemplate.from_template(BLURB_GENERATION_DB_TEMPLATE)

        QA_FIX_PROMPT = ChatPromptTemplate.from_messages([
            (
            "system",
            """
            You are **Blurb‑QA‑Repair v3**, an elite verifier/fixer for 257.328 × 450.961 inline‑only ads.
            You receive exactly one HTML snippet: <div id="blurb"> … <script> … </div>.

            ▼ TASK
            1. Parse the snippet.
            2. Audit the DESIGN‑ONLY rules below.
            3. If *all* pass → return the snippet unchanged.
            4. Else → return a single, fully‑corrected snippet that satisfies **all** rules.
            • Fix only what is broken; keep valid styling / content.
            • Aim for perfect visual appeal (balanced spacing, clear hierarchy, no overflow).
            • Output pure HTML only—no comments or explanations.

            ▼ DESIGN RULES
            SIZE
            • Root div width = 257.328 px, height = 450.961 px (exact).

            LAYOUT
            • display:flex; flex‑direction:column; justify‑content:center;
                align‑items:center; position:relative; overflow:hidden (no scrollbars).

            LAYOUT SAFETY
            • Headline font‑size ≤ 2 rem; subheading ≤ 1.3 rem  
            • line‑height: headline 1.10–1.20, sub 1.35–1.45  
            • Spacing between headline & sub: 18 ± 4 px margin‑top  
            • Headline max‑width 90 %; sub max‑width 95 %  
            • No <br> in headline—remove if present  
            • Padding ≥ 24 px on all sides; text must not touch borders

            TEXT FIT
            • If content overflows the 450.961 px height:  
                ↳ first shrink headline (≥ 1.8 rem) → sub (≥ 1.0 rem)  
                ↳ then tighten their margins  
                ↳ finally strip any remaining <br> breaks

            VISUAL HIERARCHY
            • Headline visually dominant; subheading subordinate; overall spacing balanced

            ━━ OUTPUT ━━
            Return **only** the final <div id="blurb">…</div> (with inline <script>). No extra text.
            """
            ),
            ("human", "{html}")
        ])


        chain = generation_prompt | dyn_llm | QA_FIX_PROMPT | dyn_llm

        gradient_dir, grad1, grad2 = random.choice(GRADIENTS)
        headline_font   = random.choice(HEADLINE_FONTS)
        sub_font        = random.choice(SUB_FONTS)
        anim_preset     = random.choice(ANIM_PRESETS)

        seed = {
            "gradient": f"linear-gradient({gradient_dir}, {grad1} 0%, {grad2} 100%)",
            "headline_font": headline_font,
            "sub_font": sub_font,
            "anim": anim_preset,
            "border_radius": random.randrange(10, 26),            # 10-25 px
            "border_px":      random.choice([1,2,3]),
            "border_style":   random.choice(["solid","dashed"]),
            "shadow_strength": random.choice([4,6,8]),            # px blur
            "id": secrets.token_hex(4)                            # 8-char seed id
        }

        vars_for_llm = {
            "user_prompt": prompt,
            "website_url": website_url,
            "website_content": website_data.get("content", ""),
            "gradient": seed["gradient"],
            "headline_font": seed["headline_font"],
            "sub_font": seed["sub_font"],
            "anim": seed["anim"],
            "border_radius": seed["border_radius"],
            "border_px": seed["border_px"],
            "border_style": seed["border_style"],
            "shadow_strength": seed["shadow_strength"],
            "seed_id": seed["id"],
        }

        response = await chain.ainvoke(vars_for_llm)

        # generation_prompt = ChatPromptTemplate.from_template(POWERBLURB_GENERATION_TEMPLATE)
        # chain = generation_prompt | llm

        # response = await chain.ainvoke({
        #     "user_prompt": prompt,
        #     "website_url": website_url,
        #     "website_content": website_data.get('content', ''),
        #     "seed": seed  
        # })

        response = extract_blurb(response.content)
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

def extract_blurb(html: str) -> str:
    print(f"\n\nExtracting blurb from HTML: {html}\n\n")
    m = re.search(r'(<div id="blurb"[^>]*>.*</div>)', html, re.I | re.S)
    if m:
        print(f"Extracted blurb is: {m.group(1)}\n")
        return m.group(1).strip()
    logging.warning("No <div id='blurb'> found.")
    return html            # fall back to full response

# def extract_blurb(html:str)->str:
#     print(f"\n\nExtracting blurb from HTML: {html}\n\n")
#     m = re.search(r'(<div id="blurb"[^>]*>.*?</div>)', html, re.I|re.S)
#     if m:
#         print(f"Extracted blurb is: {m.group(1)}\n")
#         return m.group(1)
#     else:
#         print(f"Could not extract blurb. Full response: {html}")
#         logging.warning("No <div id='blurb'> found in the response.")
#         return html


# POWERBLURB_GENERATION_TEMPLATE = """
# Create a complete HTML code for a visually stunning splash page ad that fits precisely within a 257.328-pixel wide by 450.961-pixel high panel, featuring a bold headline and an engaging subheading, optimized for visual impact.
# WEBSITE INFORMATION:
# Website URL: {website_url}
# Website Content: 
# {website_content}

# USER PROMPT:
# {user_prompt}


# Based on the above, generate a bold headline and an engaging subheading.
# Include all styling within a <style> tag in the HTML <head> using CSS to achieve the design. Do not include a CTA button or link; instead, enlarge and emphasize the text to fill the content area. Follow these guidelines to ensure each version is unique and creative:

# Core Requirements:
# Size: Set the body to exactly 257.328px wide and 450.961px high, with the content box filling the full dimensions (width: 100%; height: 100%) using display: flex to center text vertically and horizontally. Use padding (e.g., 20px–30px) for whitespace.
# Background: Keep the body background transparent, applying all color and visual effects within the .blurb-content-box using a unique gradient each time.
# Responsiveness: Include a @media query for max-width: 257.328px to slightly scale down text and padding if needed, ensuring consistency within the fixed size.

# Unique Variations (Randomize These Each Time):
# Color Scheme: Use a purple-dominant gradient as a base (e.g., #1a0033, #4b0082, #800080), mixed with one or two contrasting colors (e.g., cyan #00FFFF, teal #008080, gold #FFD700, magenta #FF00FF, white #FFFFFF) for the .blurb-content-box background. Vary the gradient direction (e.g., 45deg, 180deg, 270deg) and stops (e.g., 0%, 50%, 100%). Define accent colors for text shadows, borders, and underlines.
# Typography: Pair a unique, eye-catching font for the headline (e.g., 'Orbitron', 'Russo One', 'Playfair Display', 'Futura', 'Bebas Neue') with a contrasting, readable font for the subheading (e.g., 'Space Mono', 'Roboto', 'Open Sans', 'Montserrat'). Import fonts from Google Fonts via @import. Adjust font sizes, weights, and shadows (e.g., text-shadow) for diversity.
# Animations: Apply distinct @keyframes animations to:
# - Headline (e.g., bounce, fade, typewriter effect, scale).
# - Subheading (e.g., fade-in with delay, slide-up, glow).
# Content Box Styling: Vary the border (e.g., 1px–3px, solid/dashed, #FFFFFF or accent color), border-radius (e.g., 10px–25px). Experiment with opacity or layered gradients for depth.

# Creative Guidelines:
# Cosmic Themes: Each version should evoke a distinct cosmic vibe (e.g., galaxy clusters, supernova burst, starry void, nebula mist, sci-fi portal). Avoid repeating themes or styles from previous versions.
# Minimalism: Keep the design clean with ample whitespace within the gradient-filled box, ensuring a professional yet bold look.
# Uniqueness: Randomize color palettes, font pairings, shape types, animation styles, and box effects to create a fresh identity each time. For example:
# - One version might use a teal-to-purple gradient with spinning polygons and a pulsing box.
# - Another could feature a magenta-to-gold gradient with twinkling stars and a sliding headline.
# Diversity Requirement (CRITICAL): For each design element (e.g., color scheme, typography, layout, background elements, animations), randomly select one option from a provided list. Even without previous output history, each output must be generated using independent random choices to ensure a fresh and varied design every time.

# Emojis: Include 🌌 and ✨ in the HTML as specified, ensuring they integrate naturally with the text.

# CRITICAL: The generated HTML must strictly use a body width of 257.328px and a height of 450.961px—no adjustments or responsive changes are allowed.
# CRITICAL: **Incorporate Website Context**
#     - Use the provided website URL and scraped content to:
#     - Reflect relevant branding, themes, or content from the website.
#     - Integrate significant cues, or textual details from the scraped content.
#     - Ensure that the splash page resonates with the website’s overall identity.



# EXAMPLE SPLASH PAGE AD:
# <!doctype html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>Cosmic Splash Ad</title>
#     <style>
#       @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Montserrat:wght@400&display=swap');
 
#       html, body {{
#         margin: 0;
#         padding: 0;
#         width: 257.328px;
#         height: 450.961px;
#         background: transparent;
#       }}
 
#       body {{
#         display: flex;
#         align-items: center;
#         justify-content: center;
#       }}
 
#       .blurb-content-box {{
#         width: 100%;
#         height: 100%;
#         padding: 25px;
#         box-sizing: border-box;
#         background: linear-gradient(135deg, #FF00FF 0%, #008080 100%);
#         border: 2px solid #FFFFFF;
#         border-radius: 20px;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         align-items: center;
#         position: relative;
#         animation: zoomIn 1.5s ease-out;
#       }}
 
#       h1 {{
#         font-family: 'Orbitron', sans-serif;
#         font-size: 2.2rem;
#         color: #FFFFFF;
#         margin: 0;
#         text-align: center;
#         text-shadow: 0 0 6px #FFD700;
#         animation: bounceIn 1s ease-out;
#       }}
 
#       p {{
#         font-family: 'Montserrat', sans-serif;
#         font-size: 1.3rem;
#         color: #FFFFFF;
#         margin-top: 20px;
#         text-align: center;
#         text-shadow: 0 0 4px #00FFFF;
#         animation: fadeUp 1.8s ease-in-out;
#       }}
 
#       .underline {{
#         text-decoration: underline;
#         text-decoration-color: #FFD700;
#         font-weight: bold;
#       }}
 
#       .cosmic-element {{
#         position: absolute;
#         border-radius: 50%;
#         opacity: 0.3;
#         background: radial-gradient(circle, #FFFFFF 0%, #FF00FF 100%);
#         animation: float 10s infinite ease-in-out;
#       }}
 
 
#       @keyframes zoomIn {{
#         0% {{ transform: scale(0.8); opacity: 0; }}
#         100% {{ transform: scale(1); opacity: 1; }}
#       }}
 
#       @keyframes bounceIn {{
#         0% {{ transform: translateY(-50px); opacity: 0; }}
#         60% {{ transform: translateY(10px); opacity: 1; }}
#         100% {{ transform: translateY(0); }}
#       }}
 
#       @keyframes fadeUp {{
#         0% {{ transform: translateY(30px); opacity: 0; }}
#         100% {{ transform: translateY(0); opacity: 1; }}
#       }}
 
#       @keyframes float {{
#         0%, 100% {{ transform: translateY(0); }}
#         50% {{ transform: translateY(-15px); }}
#       }}
 
#       @keyframes twinkle {{
#         0%, 100% {{ opacity: 0.3; }}
#         50% {{ opacity: 0.6; }}
#       }}
 
#       @media (max-width: 257.328px) {{
#         .blurb-content-box {{
#           padding: 18px;
#         }}
#         h1 {{
#           font-size: 1.9rem;
#         }}
#         p {{
#           font-size: 1.1rem;
#         }}
#       }}

#       /* Add dark background for preview */
#       html {{
#         background: #1f2937;
#         min-height: 100vh;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#       }}
#     </style>
#   </head>
#   <body>
#     <div class="blurb-content-box">
#       <h1>Launch Your Success Into Orbit 🌌!</h1>
#       <p>Unlock <span class="underline">cosmic growth</span> with tools designed to skyrocket your business! ✨</p>
#     </div>
#   </body>
# </html>

# Provide the full HTML code, including the <style> tag with all CSS, ready to run as a standalone page. Push the boundaries of creativity while staying true to the cosmic, text-focused aesthetic, ensuring every version feels vibrant, unique, and visually engaging within the small panel.
# """


# POWERBLURB_REFINEMENT_TEMPLATE = """
# You are an expert digital designer who refines Hercu/PowerBlurbs to enhance visual impact and creativity.

# Your task is to refine the existing HTML splash page ad based on the user's feedback in triple backticks.

# ORIGINAL POWERBLURB:
# {previous_blurb}

# USER FEEDBACK FOR REFINEMENT:
# ```{user_prompt}```

# Please apply the following guidelines, ensuring the final design remains within a 257.328-pixel wide by 450.961-pixel high panel and retains the cosmic, text-focused aesthetic described previously.

# THESE WERE THE ORIGINAL GUIDELINES FOR THE BLURB GENERATION (FOR REFERENCE):
# Include all styling within a <style> tag in the HTML <head> using CSS to achieve the design. Do not include a CTA button or link; instead, enlarge and emphasize the text to fill the content area. Follow these guidelines to ensure each version is unique and creative:

# Core Requirements:
# Size: Set the body to exactly 257.328px wide and 450.961px high, with the content box filling the full dimensions (width: 100%; height: 100%) using display: flex to center text vertically and horizontally. Use padding (e.g., 20px–30px) for whitespace.
# Background: Keep the body background transparent, applying all color and visual effects within the .blurb-content-box using a unique gradient each time.
# Responsiveness: Include a @media query for max-width: 257.328px to slightly scale down text and padding if needed, ensuring consistency within the fixed size.

# Unique Variations (Randomize These Each Time):
# Color Scheme: Use a purple-dominant gradient as a base (e.g., #1a0033, #4b0082, #800080), mixed with one or two contrasting colors (e.g., cyan #00FFFF, teal #008080, gold #FFD700, magenta #FF00FF, white #FFFFFF) for the .blurb-content-box background. Vary the gradient direction (e.g., 45deg, 180deg, 270deg) and stops (e.g., 0%, 50%, 100%). Define accent colors for text shadows, borders, and underlines.
# Typography: Pair a unique, eye-catching font for the headline (e.g., 'Orbitron', 'Russo One', 'Playfair Display', 'Futura', 'Bebas Neue') with a contrasting, readable font for the subheading (e.g., 'Space Mono', 'Roboto', 'Open Sans', 'Montserrat'). Import fonts from Google Fonts via @import. Adjust font sizes, weights, and shadows (e.g., text-shadow) for diversity.
# Background Elements: Add 1–3 dynamic shapes (e.g., stars, circles, polygons, waves) as <div>s with classes like .cosmic-element. Style with CSS properties (e.g., radial-gradient, border-radius, opacity: 0.2–0.4) and position absolutely (e.g., top, left, bottom, right). Vary their size (100px–200px) and placement each time.
# Animations: Apply distinct @keyframes animations to:
# - .blurb-content-box (e.g., slide-in from top/bottom, zoom-in, pulse, rotate slightly).
# - Headline (e.g., bounce, fade, typewriter effect, scale).
# - Subheading (e.g., fade-in with delay, slide-up, glow).
# - Background elements (e.g., spin, float, twinkle, orbit) with unique durations (e.g., 5s–12s) and easing (e.g., linear, ease-in-out).
# Content Box Styling: Vary the border (e.g., 1px–3px, solid/dashed, #FFFFFF or accent color), border-radius (e.g., 10px–25px), and box-shadow (e.g., glow, soft, bold with accent color). Experiment with opacity or layered gradients for depth.

# Creative Guidelines:
# Cosmic Themes: Each version should evoke a distinct cosmic vibe (e.g., galaxy clusters, supernova burst, starry void, nebula mist, sci-fi portal). Avoid repeating themes or styles from previous versions.
# Minimalism: Keep the design clean with ample whitespace within the gradient-filled box, ensuring a professional yet bold look.
# Uniqueness: Randomize color palettes, font pairings, shape types, animation styles, and box effects to create a fresh identity each time. For example:
# - One version might use a teal-to-purple gradient with spinning polygons and a pulsing box.
# - Another could feature a magenta-to-gold gradient with twinkling stars and a sliding headline.
# Diversity Requirement (CRITICAL): For each design element (e.g., color scheme, typography, layout, background elements, animations), randomly select one option from a provided list. Even without previous output history, each output must be generated using independent random choices to ensure a fresh and varied design every time.

# Emojis: Include 🌌 and ✨ in the HTML as specified, ensuring they integrate naturally with the text.

# CRITICAL: The generated HTML must strictly use a body width of 257.328px and a height of 450.961px—no adjustments or responsive changes are allowed.

# Provide the complete HTML code, including a <style> tag with all CSS, ready to run as a standalone page. Do not include any explanations or notes outside the HTML code.
# """
