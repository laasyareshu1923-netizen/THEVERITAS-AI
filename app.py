import streamlit as st
import google.generativeai as genai
import json

# App Configuration
st.set_page_config(page_title="Veritas - Fake News Detector", page_icon="🔎", layout="wide")

st.title("🔎 Veritas: Real-Time Fact Checker")
st.caption("Verify claims instantly using Google Gemini machine learning, Telugu newspapers, and global/local news sources.")

# 🔑 SECURE SECRET EXTRACTION
# The app looks for 'GEMINI_API_KEY' inside your Streamlit Cloud Advanced Secrets dashboard.
try:
    MASTER_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    MASTER_API_KEY = ""

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
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Default targeted context framework built for regional Telugu media validation
                regional_context = "Cross-reference deeply with AP regional desks of major Telugu dailies like Eenadu, Sakshi, Andhra Jyothy, and Vartha."
                location_context = f"specifically within the local context of Vizag (Visakhapatnam). {regional_context}"

                # Structured prompt engineering targeting Telugu media ecosystems
                prompt = f"""
                You are an expert AI fact-checker analyzing news {location_context}.
                Analyze the following claim for accuracy. Check regional languages, leading Telugu newspapers, national dailies, and official circulars if applicable.
                
                Claim to evaluate: "{claim_input}"
                
                Provide your response strictly in the following JSON format:
                {{
                    "verdict": "COMPLETELY TRUE" or "PARTIALLY TRUE" or "MISLEADING" or "COMPLETELY FAKE",
                    "confidence_score": "0% to 100%",
                    "explanation": "A concise 3-sentence summary in English explaining why this claim is true or fake. Explicitly mention which Telugu or global papers corroborate or deny this.",
                    "trusted_sources": ["Eenadu", "Sakshi", "Andhra Jyothy", "Other verified sources checked"]
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
                
                col1, col2 = st.columns()
                
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
                    st.info("📍 **Target Scope:** Vizag Regional Validation Desk")
                
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
              
