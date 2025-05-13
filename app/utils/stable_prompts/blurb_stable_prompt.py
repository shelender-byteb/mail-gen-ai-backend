

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