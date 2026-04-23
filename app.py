
import streamlit as st
from groq import Groq
import time
import re
from fpdf import FPDF

# ---------------- CONFIG ----------------
MODEL = "llama-3.1-8b-instant"

# Secure API key (Streamlit Cloud Secrets)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# ---------------- SAFE GENERATE ----------------
def safe_generate(prompt):
    for _ in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception:
            time.sleep(2)

    return "Server busy, try again later."


# ---------------- AGENTS ----------------

def research_agent(prompt):
    return safe_generate(f"""
You are a Travel Research Agent.

User Query:
{prompt}

Tasks:
- Identify destination
- Provide overview
- Best time to visit
- Travel tips
""")


def places_agent(prompt):
    return safe_generate(f"""
You are a Travel Activities Agent.

User Query:
{prompt}

Tasks:
- Suggest top places
- Adventure activities
- Nightlife
- Religious places
- Relaxation spots
""")


def hotel_agent(prompt):
    return safe_generate(f"""
You are a Hotel & Food Agent.

User Query:
{prompt}

Tasks:
- Budget hotels
- Mid-range hotels
- Restaurants
""")


def budget_agent(prompt):
    return safe_generate(f"""
You are a Budget Planning Agent.

User Query:
{prompt}

Tasks:
- Estimate total cost
- Break into Stay, Food, Travel, Activities
""")


def planner_agent(prompt, research, places, hotels, budget):
    return safe_generate(f"""
You are a Travel Planner Agent.

User Query:
{prompt}

Research:
{research}

Places:
{places}

Hotels:
{hotels}

Budget:
{budget}

Tasks:
- Create day-wise itinerary
- Include Morning, Afternoon, Evening
- Maintain budget
""")


# ---------------- PDF FUNCTION ----------------
def generate_pdf(text):
    # remove emojis (fix FPDF crash)
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    # Title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Travel Itinerary", ln=True)

    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    file_path = "itinerary.pdf"
    pdf.output(file_path)
    return file_path


# ---------------- PIPELINE ----------------
def generate_trip(prompt):
    research = research_agent(prompt)
    places = places_agent(prompt)
    hotels = hotel_agent(prompt)
    budget = budget_agent(prompt)
    itinerary = planner_agent(prompt, research, places, hotels, budget)
    return itinerary


# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="AI Travel Planner", layout="wide")

st.title("🌍 AI Travel Planner (Multi-Agent)")

user_input = st.text_input("Enter your travel plan")

if st.button("Generate Plan"):

    with st.spinner("Agents working..."):
        result = generate_trip(user_input)

    # display result
    formatted = result.replace("\n", "<br>")
    st.markdown(f"""
    <div style="
        background:#111;
        color:white;
        padding:20px;
        border-radius:10px;
        line-height:1.6;
    ">
    {formatted}
    </div>
    """, unsafe_allow_html=True)

    # PDF download
    pdf_file = generate_pdf(result)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Download Itinerary as PDF",
            data=f,
            file_name="travel_plan.pdf",
            mime="application/pdf"
        )
```

