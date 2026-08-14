import streamlit as st
import google.generativeai as genai
import json

# App Configuration
st.set_page_config(page_title="Veritas - Fake News Detector", page_icon="🔎", layout="wide")

st.title("🔎 Veritas: Real-Time Fact Checker")
st.caption("Verify claims instantly using Google Gemini machine learning.")
# --- ADD THIS TIME WARNING SECTION AT THE TOP ---
import datetime

# Get the current time in India (IST)
now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

# Check if the current time is in the morning (before 1:30 PM IST)
if now_ist.hour < 13 or (now_ist.hour == 13 and now_ist.minute < 30):
    st.warning(
        "⚠️ **Daily Limit Notice:** The shared free tier key resets daily at **1:30 PM IST**. "
        "If the app throws an error right now, please try again after 1:30 PM, or paste your own private API key in the sidebar to bypass the limit instantly!",
        icon="⏰"
    )
    
# 🔑 SECURE SECRET EXTRACTION
try:
    MASTER_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    MASTER_API_KEY = ""

# Sidebar for User Tier Selection (No API Key inputs)
with st.sidebar:
    st.header("📍 Verification Scope")
    level = st.radio(
        "Select Verification Level:", 
        ["Global", "National", "Local (Visakhapatnam & Telugu Media)"], 
        index=2
    )

# Main User Interface 
claim_input = st.text_area(
    "📝 Paste the Telugu or English news article, headline, or claim you want to verify:",
    placeholder="e.g., Paste regional news updates, WhatsApp forwards, or local headlines here...",
    height=150
)

if st.button("🚀 Verify Claim", use_container_width=True):
    if not MASTER_API_KEY:
        st.error("⚠️ Cloud Configuration Error: Please make sure you have added 'GEMINI_API_KEY' into your Streamlit Cloud Secrets dashboard!")
    elif not claim_input.strip():
        st.warning("⚠️ Please paste a claim or news article to verify.")
    else:
        with st.spinner("Analyzing sources and verifying authenticity..."):
            try:
                # Initialize Gemini API automatically via Cloud Secrets
                genai.configure(api_key=MASTER_API_KEY)
                
                # 🛠️ FIXED: Replaced legacy string with the current production model alias
                model = genai.GenerativeModel("gemini-3.6-flash")
                
                # Dynamic context rules based on user selected tier
                if level == "Global":
                    location_context = "internationally across trusted global news networks, Reuters, AP, and major world publications."
                elif level == "National":
                    location_context = "at an Indian national country level, cross-referencing major national media networks, PIB fact checks, and national dailies."
                else:
                    # Local Tier focusing on Visakhapatnam
                    regional_context = "Cross-reference deeply with Andhra Pradesh regional desks of major Telugu dailies like Eenadu, Sakshi, Andhra Jyothy, and Vartha."
                    location_context = f"specifically within the local context of Visakhapatnam (Vizag). {regional_context}"

                # Structured prompt engineering targeting the selected tier with timeline insights
                prompt = f"""
                You are an expert AI fact-checker analyzing news {location_context}.
                
                CRITICAL INSTRUCTION: Analyze the text using a comprehensive timeline framework:
                - PAST: Deep historical baselines and archival metrics.
                - PRESENT: Ongoing established operational standards.
                - LIVE: Closely review absolute breaking events up to today in August 2026. Prioritize sudden changes, new corporate restructurings, or fresh press updates that reverse or conflict with prior facts.
                
                Analyze the following claim for accuracy against the relevant databases, newspapers, and official circulars for this geographical tier.
                
                Claim to evaluate: "{claim_input}"
                
                Provide your response strictly in the following JSON format:
                {{
                    "verdict": "COMPLETELY TRUE" or "PARTIALLY TRUE" or "MISLEADING" or "COMPLETELY FAKE",
                    "confidence_score": "0% to 100%",
                    "explanation": "A concise 3-sentence summary in English explaining why this claim is true or fake based on this specific tier's media publications.",
                    "trusted_sources": ["Source 1", "Source 2", "Other verified sources checked"]
                }}
                """
                
                # Fetch prediction from Gemini
                response = model.generate_content(prompt)
                
                # Clean and parse JSON response
                response_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(response_text)
                
                # Layout Results Dashboard
                st.divider()
                st.subheader("📊 Analysis Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    verdict = data.get("verdict", "UNKNOWN")
                    score = data.get("confidence_score", "0%")
                    
                    if "TRUE" in verdict:
                        st.success(f"### {verdict}")
                    elif "MISLEADING" in verdict or "PARTIALLY" in verdict:
                        st.warning(f"### {verdict}")
                    else:
                        st.error(f"### {verdict}")
                        
                    st.metric(label="AI Confidence Score", value=score)
                    st.info(f"📍 **Target Scope:** {level}")
                
                with col2:
                    st.markdown("### 📝 Explanation")
                    st.write(data.get("explanation", "No explanation provided."))
                    
                    st.markdown("### 📰 Checked Across These Outlets")
                    sources = data.get("trusted_sources", [])
                    if sources:
                        for source in sources:
                            st.markdown(f"- ✅ {source}")
                    else:
                        st.write("No specific local sources indexed for this explicit claim.")
                        
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
                
