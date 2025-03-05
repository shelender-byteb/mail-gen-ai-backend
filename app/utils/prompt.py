from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


PROMPT_TEMPLATE = """
You are an expert web developer specializing in creating **splash pages**.
Your task is to generate a **complete HTML file** with embedded CSS in a `<style>` tag. The code should be standalone, fully responsive, and visually appealing based on the user's input and style type.

### **User Input**
- **Style Type:** {style_type} *(Either "professional" or "casual")*
- **User Description:** {user_input}

---

### **Guidelines**
1. **Include ALL CSS** inside `<style>` tags within the `<head>`.
2. **Ensure responsiveness** so the page adapts to different screen sizes.
3. **Incorporate animations subtly** (for "professional") or dynamically (for "casual").
4. **Match the color scheme** to the style type:
   - **Professional:** Elegant, muted tones (e.g., navy blue, silver, dark green).
   - **Casual:** Vibrant, playful colors with gradients.
5. **Mandatory elements:**
   - A **main headline**.
   - A **subheading**.
   - A **CTA button** (e.g., "Discover More" or "Get Started").
6. **Follow typography best practices:**
   - Professional: Serif fonts like `Georgia`, `Montserrat`, `Lora`.
   - Casual: Modern fonts like `Orbitron`, `Poppins`, `Raleway`.
7. **Ensure code structure follows best practices** for readability and maintainability.

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
"""





prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an expert web developer specializing in creating **splash pages**.
        Your task is to generate a **complete HTML file** with embedded CSS in a `<style>` tag. The code should be standalone, fully responsive, and visually appealing based on the user's input and style type.

        You will be given the following details in each query:
        - **Style Type:** *(Either "professional" or "casual")*
        - **User Description:** *(A brief description of the splash page requirements)*


        ---

        ### **Guidelines**
        1. **Include ALL CSS** inside `<style>` tags within the `<head>`.
        2. **Ensure responsiveness** so the page adapts to different screen sizes.
        3. **Incorporate animations subtly** (for "professional") or dynamically (for "casual").
        4. **Match the color scheme** to the style type:
        - **Professional:** Elegant, muted tones (e.g., navy blue, silver, dark green).
        - **Casual:** Vibrant, playful colors with gradients.
        5. **Mandatory elements:**
        - A **main headline**.
        - A **subheading**.
        - A **CTA button** (e.g., "Discover More" or "Get Started").
        6. **Follow typography best practices:**
        - Professional: Serif fonts like `Georgia`, `Montserrat`, `Lora`.
        - Casual: Modern fonts like `Orbitron`, `Poppins`, `Raleway`.
        7. **Ensure code structure follows best practices** for readability and maintainability.

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
        ("human", "User Query:\nStyle Type: {style_type}\nDescription: {user_input}")
        ])





OLD_TEMPLATE = """
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