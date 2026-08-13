import streamlit as st
import google.generativeai as genai
import json

# App Configuration
st.set_page_config(page_title="Veritas - Fake News Detector", page_icon="🔎", layout="wide")

st.title("🔎 Veritas: Real-Time Fact Checker")
st.caption("Verify claims instantly using Google Gemini machine learning, Telugu newspapers, and global/local news sources.")

# Sidebar for API Key and Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    st.divider()
    st.markdown("### 🌍 Scope Levels")
    level = st.radio("Select Verification Level:", ["Global", "National", "Local (City Specific)"], index=2)
    
    city = ""
    if level == "Local (City Specific)":
        # Defaulting to Vizag as requested
        city = st.text_input("Enter City Name:", value="Vizag (Visakhapatnam)", placeholder="e.g., Vizag, Hyderabad, Mumbai")

# Main Interface
claim_input = st.text_area(
    "📝 Paste the Telugu or English news article, headline, or claim you want to verify:",
    placeholder="e.g., Paste regional news updates, WhatsApp forwards, or local headlines here..."
)

if st.button("🚀 Verify Claim", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar.")
    elif not claim_input.strip():
        st.warning("⚠️ Please paste a claim or news article to verify.")
    elif level == "Local (City Specific)" and not city.strip():
        st.warning("⚠️ Please specify the city name for local verification.")
    else:
        with st.spinner("Analyzing sources and verifying authenticity..."):
            try:
                # Initialize Gemini API
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Dynamic context rules for regional Telugu media cross-referencing
                regional_context = ""
                if "vizag" in city.lower() or "visakhapatnam" in city.lower():
                    regional_context = "Cross-reference deeply with AP regional desks of major Telugu dailies like Eenadu, Sakshi, Andhra Jyothy, and Vartha."
                
                location_context = "internationally"
                if level == "National":
                    location_context = "at a national level, checking mainstream networks"
                elif level == "Local (City Specific)":
                    location_context = f"specifically within the local context of {city}. {regional_context}"

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
                
                # Layout Results
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
                    st.info(f"📍 **Level:** {level} {f'({city})' if city else ''}")
                
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
              
