from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder




prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an expert web developer specializing in creating **splash pages**.
        Your task is to generate a **complete HTML file** with embedded CSS in a `<style>` tag. The code should be standalone, fully responsive, and visually appealing based on the user's input and style type.

        You will be given the following details in each query:
        - **Style Type:** *(Either "professional" or "casual")*
        - **User Description:** *(A brief description of the splash page requirements)*
        - **Operation:** *(Either "start_over" to create a new page or "update" to modify existing code)*
        - **Previous HTML:** *(When operation is "update", this contains the HTML to modify)*
        - **Button URL:** *(URL to associate with the CTA button - should open in a new tab)*

        ---

        ### **Guidelines**
        1. **Include ALL CSS** inside `<style>` tags within the `<head>`.
        2. **Ensure responsiveness** so the page adapts to different screen sizes.
        3. **Incorporate animations subtly** (for "professional") or dynamically (for "casual").
        4. **Match the color scheme** to the style type:
        - **Professional:** Elegant, muted tones (e.g., navy blue, silver, dark green).
        - **Casual:** Vibrant, cosmic colors with bold gradients. Make casual themes truly cosmic with space imagery, galaxy effects, and star-like animations.
        5. **Mandatory elements:**
        - A **main headline**.
        - A **subheading**.
        - A **CTA button** that links to the provided URL and opens in a new tab (use target="_blank").
        6. **Follow typography best practices:**
        - Professional: Serif fonts like `Georgia`, `Montserrat`, `Lora`.
        - Casual: Modern fonts like `Orbitron`, `Poppins`, `Raleway`.
        7. **Ensure code structure follows best practices** for readability and maintainability.
        8. **For "update" operations:**
        - Preserve the overall structure and design elements
        - Focus only on applying the requested changes
        - Comment your changes to make them clear


        ---

        ### **Example 1: Casual Theme (Cosmic)**
        #### **Prompt:**
        *"Create another mind-blowing HTML splash page with a completely unique cosmic theme. Use the following text: Headline - 'Launch Your Success Into Orbit 🌌!', Subheading - 'Unlock cosmic growth with tools designed to skyrocket your business! ✨', CTA - 'BLAST OFF NOW!'. Introduce a unique cosmic concept (e.g., black hole distortion, alien signal transmission) with at least three animated effects."*

        #### **Expected Output:**
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Launch Your Success Into Orbit 🌌!</title>
            <style>
                /* General Reset */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Orbitron', sans-serif;
                    background: linear-gradient(135deg, rgba(25, 25, 112, 0.9), rgba(75, 0, 130, 0.9));
                    color: white;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                    position: relative;
                }}

                /* Cosmic Background Animation */
                .cosmic-background {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: radial-gradient(circle, rgba(34, 193, 195, 1) 0%, rgba(253, 187, 45, 1) 100%);
                    animation: cosmicPulse 10s infinite ease-in-out;
                    z-index: -1;
                }}

                /* Warping Grid Animation */
                .grid {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 300px;
                    height: 300px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    animation: warpGrid 8s infinite linear;
                    transform-origin: center;
                }}

                @keyframes warpGrid {{
                    0% {{
                        transform: rotate(0deg) scale(1);
                    }}
                    50% {{
                        transform: rotate(180deg) scale(1.5);
                    }}
                    100% {{
                        transform: rotate(360deg) scale(1);
                    }}
                }}

                /* Shimmering Tendrils Animation */
                .tendril {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    background: rgba(0, 255, 255, 0.5);
                    box-shadow: 0 0 15px rgba(0, 255, 255, 0.7);
                    animation: shimmer 3s infinite ease-in-out;
                    z-index: -2;
                }}

                @keyframes shimmer {{
                    0% {{
                        transform: scale(1);
                        opacity: 0.6;
                    }}
                    50% {{
                        transform: scale(1.2);
                        opacity: 0.8;
                    }}
                    100% {{
                        transform: scale(1);
                        opacity: 0.6;
                    }}
                }}

                /* Fractal Burst Animation */
                .fractals {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 200px;
                    height: 200px;
                    background: transparent;
                    border-radius: 50%;
                    animation: fractalBurst 6s infinite cubic-bezier(0.25, 0.8, 0.25, 1);
                    z-index: -1;
                }}

                @keyframes fractalBurst {{
                    0% {{
                        transform: scale(0.8);
                        opacity: 0.2;
                    }}
                    50% {{
                        transform: scale(1.5);
                        opacity: 0.8;
                    }}
                    100% {{
                        transform: scale(0.8);
                        opacity: 0.2;
                    }}
                }}

                /* Content Box */
                .content {{
                    text-align: center;
                    background-color: rgba(0, 0, 0, 0.6);
                    border-radius: 15px;
                    padding: 40px;
                    box-shadow: 0 4px 10px rgba(255, 255, 255, 0.2);
                }}

                .headline {{
                    font-size: 3rem;
                    margin-bottom: 20px;
                    color: white;
                    text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
                }}

                .subheading {{
                    font-size: 1.5rem;
                    margin-bottom: 30px;
                    color: rgba(255, 255, 255, 0.9);
                }}

                /* Button */
                .cta-button {{
                    padding: 20px 40px;
                    font-size: 1.5rem;
                    color: white;
                    background: linear-gradient(135deg, rgba(34, 193, 195, 1), rgba(253, 187, 45, 1));
                    border: none;
                    border-radius: 50px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 0 20px rgba(0, 255, 255, 0.7);
                }}

                .cta-button:hover {{
                    background: linear-gradient(135deg, rgba(253, 187, 45, 1), rgba(34, 193, 195, 1));
                    transform: scale(1.1);
                    box-shadow: 0 0 30px rgba(255, 255, 255, 0.9);
                }}

                /* Responsive Design */
                @media (max-width: 768px) {{
                    .headline {{
                        font-size: 2.5rem;
                    }}

                    .subheading {{
                        font-size: 1.25rem;
                    }}

                    .cta-button {{
                        font-size: 1.25rem;
                    }}
                }}

            </style>
        </head>
        <body>

            <!-- Cosmic Background -->
            <div class="cosmic-background"></div>

            <!-- Warping Grid -->
            <div class="grid"></div>

            <!-- Shimmering Tendrils -->
            <div class="tendril"></div>

            <!-- Fractal Burst -->
            <div class="fractals"></div>

            <!-- Content Box -->
            <div class="content">
                <div class="headline">Launch Your Success Into Orbit 🌌!</div>
                <div class="subheading">Unlock cosmic growth with tools designed to skyrocket your business! ✨</div>
                <button class="cta-button">BLAST OFF NOW!</button>
            </div>

        </body>
        </html>```

        Example 2: Professional Theme (Banking/Corporate)  
        Prompt:  
        "Create a professional splash page for a high-end law firm or financial institution. Use refined typography and a polished layout. Headline: 'Company Name', Tagline: 'Excellence. Integrity. Trust.', and a CTA button labeled 'Discover More'."  

        Expected Output:  
        ```
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Company Name - Excellence. Integrity. Trust.</title>
            <style>
                /* Reset some default styles */
                body, h1, h2, p, ul, li {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Georgia', serif;
                }}
                body {{
                    background: linear-gradient(135deg, #2a3d7b, #1f4b7d);
                    color: #fff;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    text-align: center;
                    overflow: hidden;
                }}
                .container {{
                    width: 90%;
                    max-width: 1200px;
                    padding: 40px;
                    border-radius: 12px;
                    background-color: rgba(0, 0, 0, 0.5);
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                    animation: fadeIn 2s ease-out;
                }}
                h1 {{
                    font-size: 3.5em;
                    font-weight: bold;
                    color: #d6a31d;
                    margin-bottom: 10px;
                    animation: fadeIn 1s ease-out;
                }}
                h2 {{
                    font-size: 1.5em;
                    color: #b0b0b0;
                    margin-bottom: 20px;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 300;
                    animation: fadeIn 1.5s ease-out;
                }}
                p {{
                    font-size: 1.1em;
                    color: #b0b0b0;
                    margin-bottom: 30px;
                    animation: fadeIn 2s ease-out;
                }}
                ul {{
                    list-style: none;
                    margin: 0;
                    padding: 0;
                    font-size: 1.1em;
                    color: #e0e0e0;
                    animation: fadeIn 2.5s ease-out;
                }}
                li {{
                    margin-bottom: 15px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 15px 30px;
                    font-size: 1.2em;
                    font-family: 'Montserrat', sans-serif;
                    color: #fff;
                    background-color: #d6a31d;
                    border: 2px solid #d6a31d;
                    text-decoration: none;
                    text-transform: uppercase;
                    border-radius: 5px;
                    transition: all 0.3s ease;
                    margin-top: 20px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }}
                .btn:hover {{
                    background-color: transparent;
                    color: #d6a31d;
                    transform: scale(1.1);
                    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
                }}
                @keyframes fadeIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                @media (max-width: 768px) {{
                    h1 {{
                        font-size: 2.5em;
                    }}
                    h2 {{
                        font-size: 1.2em;
                    }}
                    .container {{
                        padding: 20px;
                    }}
                    .btn {{
                        font-size: 1em;
                        padding: 12px 24px;
                    }}
                }}
            </style>
        </head>
        <body>

            <div class="container">
                <h1>Company Name</h1>
                <h2>Excellence. Integrity. Trust.</h2>
                <p>At Company Name, we are committed to providing exceptional services to help you navigate the complexities of the modern world. We build long-term relationships based on trust and professionalism.</p>
                
                <ul>
                    <li><strong>Expert Advice:</strong> Our team of professionals offers tailored solutions to meet your unique needs.</li>
                    <li><strong>Client-Centered Focus:</strong> We prioritize your goals and put your interests first at every step.</li>
                    <li><strong>Unwavering Integrity:</strong> We stand by our values and maintain the highest ethical standards.</li>
                </ul>
                
                <a href="#" class="btn">Discover More</a>
            </div>

        </body>
        </html>```
        """),
       ("human", """
        User Query:
        Style Type: {style_type}
        Description: {user_input}
        Operation: {operation}
        Button URL: {button_url}
        
        Previous HTML (if the Operation is update): {previous_html}
        """)
        ])





PROMPT_TEMPLATE = """
You are an expert web developer specializing in creating splash pages. 
Generate a complete HTML/CSS code based on the user's description and selected style.

Style type: {style_type}
User description: {user_input}


Guidelines:
1. Include ALL CSS in <style> tags
2. Use responsive design
3. Add subtle animations
4. Ensure color scheme matches the style type
5. Include a main headline, subheading, and CTA button
6. Make it a complete standalone HTML file

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




EMAIL_GENERATION_TEMPLATE = """
    You are an expert email marketing specialist who creates compelling, conversion-focused email advertisements.

    Your task is to generate a professional email advertisement based on the website content and user prompt provided below.

    WEBSITE INFORMATION:
    Website URL: {website_url}
    Website Content: 
    {website_content}

    USER PROMPT:
    {user_prompt}

    GUIDELINES:
    1. Create a compelling subject line that entices recipients to open the email
    2. Use a friendly, professional tone that matches the company's industry and branding
    3. Include a clear value proposition early in the email
    4. Be highly creative with the email structure - don't follow a standard formula but ALWAYS GIVE A SUBJECT LINE IN THE BEGINNING
    5. Use plenty of emojis throughout the email to make it eye-catching and engaging ✨🚀💯
    6. Experiment with different formatting styles including bullet points, bold text, and varied paragraph lengths
    7. Create a visually dynamic email that stands out in an inbox
    8. Make the tone exciting and energetic - this is marketing that needs to grab attention immediately
    9. Add a strong call-to-action that directs recipients to the website
    10. Keep the email concise (250-400 words maximum)
    11. DO NOT include any headers, footers, or salutations (no "Dear" or "Hello" openings)
    12. Include provided website URL {website_url} as contact details in the end in the section of response [Contact info with website URL]
    13. Use only the provided website URL {website_url} in the email as the primary link for all call-to-actions, not any links from the scraped content
    14. ONLY GIVE RESPONSE IN MARKDOWN FORMAT. NEVER GIVE RESPONSE IN HTML FORMAT.
    15. For the contact information at the end, simply write "Visit us:" followed by the website URL {website_url}. Do not include the text "[Contact info with website URL]" in your response.

    FORMAT YOUR RESPONSE:
    SUBJECT: [Your engaging subject line with emojis]

    [Creative email body with varied formatting, multiple emojis, and eye-catching elements]

    [Contact info with website URL]

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
    would fall down?<contact@domain>
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
3. Ensure the subject line remains compelling and includes emojis
4. Keep the overall tone consistent with the brand while maintaining an exciting, energetic style
5. Maintain a clear call-to-action that links to the provided website URL
6. Ensure the email remains concise (250-400 words maximum)
7. ONLY GIVE RESPONSE IN MARKDOWN FORMAT. NEVER GIVE RESPONSE IN HTML FORMAT.
8. Preserve or enhance the creative formatting of the original email
9. Maintain or add more emojis to keep the email eye-catching and engaging
10. DO NOT add salutations (no "Dear" or "Hello" openings) if they weren't in the original



FORMAT YOUR RESPONSE:
SUBJECT: [Updated subject line if needed]

[Refined email body]

[Contact info with website URL]

Do not include any explanations or notes outside the email format.
"""








##########################################################



"""
EXAMPLES OF GOOD STYLING & FORMAT:
Here are three examples to guide you on structure only. DO NOT copy these exact designs or content. \
Instead, be creative and develop unique styling that matches the company's branding and purpose. These are just to show potential layout approaches:

Example 1:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Make 2025 Historic For You!</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #F9F9F9;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
            color: #E63946;
        }}
        .highlight {{
            background-color: #FFEDCC;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #FFC107;
        }}
        .promo-code {{
            font-size: 24px;
            font-weight: bold;
            color: #E63946;
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background-color: #F8F9FA;
            border-radius: 5px;
            border: 2px dashed #E63946;
        }}
        .features {{
            margin: 20px 0;
        }}
        .feature {{
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
        }}
        .feature:before {{
            content: "►";
            position: absolute;
            left: 0;
            color: #E63946;
        }}
        .cta {{
            text-align: center;
            margin: 30px 0 20px;
        }}
        .button {{
            display: inline-block;
            background-color: #E63946;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 18px;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: #D62B39;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 14px;
            text-align: center;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Email content -->
    </div>
</body>
</html>
```

Example 2:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Super Hot Opportunity - Make 2025 Historic!</title>
    <style>
        body {{
            font-family: 'Trebuchet MS', sans-serif;
            line-height: 1.6;
            color: #2E2E2E;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #F0F2F5;
        }}
        .container {{
            background: linear-gradient(135deg, #6A11CB 0%, #2575FC 100%);
            border-radius: 15px;
            padding: 5px;
        }}
        .content {{
            background-color: white;
            border-radius: 12px;
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        .header h1 {{
            color: #6A11CB;
            margin-bottom: 10px;
            font-size: 32px;
        }}
        .header h2 {{
            color: #2575FC;
            font-size: 24px;
            font-weight: 500;
            margin-top: 0;
        }}
        .promo-box {{
            background: linear-gradient(45deg, #FF9A9E 0%, #FAD0C4 99%, #FAD0C4 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 25px 0;
            text-align: center;
        }}
        .promo-code {{
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 2px;
            color: #6A11CB;
            margin: 15px 0;
            padding: 10px 15px;
            background-color: white;
            display: inline-block;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .features-container {{
            background-color: #F8F9FA;
            border-radius: 10px;
            padding: 20px 30px;
            margin: 25px 0;
        }}
        .feature {{
            position: relative;
            padding: 8px 0 8px 35px;
            margin: 10px 0;
        }}
        .feature:before {{
            content: "✨";
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
        }}
        .emoji {{
            font-size: 1.2em;
            vertical-align: middle;
        }}
        .price {{
            font-size: 24px;
            font-weight: bold;
            color: #2575FC;
            margin: 20px 0;
            text-align: center;
        }}
        .cta {{
            text-align: center;
            margin: 30px 0;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(to right, #6A11CB 0%, #2575FC 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 18px;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.4);
        }}
        .button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(37, 117, 252, 0.5);
        }}
        a {{
            color: #2575FC;
            text-decoration: none;
            border-bottom: 1px dotted;
        }}
        .highlight {{
            background: linear-gradient(120deg, rgba(255,194,102,0.2) 0%, rgba(255,194,102,0.2) 100%);
            background-repeat: no-repeat;
            background-size: 100% 40%;
            background-position: 0 85%;
            padding: 0 5px;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #777;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <!-- Email content -->
        </div>
    </div>
</body>
</html>
```
"""











# DO NOT copy exact styles, colors, or layout from the from the examples.

# FORMAT YOUR HTML RESPONSE:
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>[Your Email Subject Line]</title>
#     <style>
#         /* Include your complete CSS styling here */
#         body {{
#             font-family: 'Arial', sans-serif;
#             line-height: 1.6;
#             color: #333;
#             max-width: 600px;
#             margin: 0 auto;
#             padding: 20px;
#             background-color: #F9F9F9;
#         }}
#         /* Add more styles as needed */
#     </style>
# </head>
# <body>
#     <div class="container">
#         <!-- Your email content here -->
#         <div class="header">
#             <h1>[Your main headline]</h1>
#         </div>
        
#         <!-- Main content -->
        
#         <!-- Call to action -->
#         <div class="cta">
#             <a href="{website_url}" class="button">Your CTA Text</a>
#         </div>
        
#         <!-- Footer -->
#         <div class="footer">
#             <p>© 2025 [Company Name]. All rights reserved.</p>
#         </div>
#     </div>
# </body>
# </html>