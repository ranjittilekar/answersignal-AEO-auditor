import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai
import re
import pandas as pd
from urllib.parse import urlparse

# Set up page config
st.set_page_config(page_title="AnswerSignal: The AEO & Discovery Auditor", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# Inject Custom CSS for subtle improvements
st.markdown("""
    <style>
        /* Custom progress bar color for score */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #f44336, #ffeb3b, #4caf50);
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #E0E0E0;
            margin-bottom: -1rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #9E9E9E;
            margin-bottom: 2rem;
        }
        .stAlert {
            background-color: #262730;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_aeo_signals(url):
    """Fetches the page and extracts SEO/AEO signals."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Signals
    title = soup.title.string if soup.title else None
    
    meta_desc = None
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        meta_desc = desc_tag.get('content')
        
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
    h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
    
    # Extract Additional Signals
    canonical_tag = soup.find('link', rel='canonical')
    canonical_url = canonical_tag.get('href') if canonical_tag else None
    
    og_title_tag = soup.find('meta', property='og:title')
    og_title = og_title_tag.get('content') if og_title_tag else None
    
    og_desc_tag = soup.find('meta', property='og:description')
    og_desc = og_desc_tag.get('content') if og_desc_tag else None
    
    text_content = soup.get_text(separator=' ', strip=True)
    word_count = len(text_content.split())
    
    # Extract JSON-LD Schema
    schema_data = []
    schemas = soup.find_all('script', type='application/ld+json')
    for script in schemas:
        try:
            if script.string:
                schema_data.append(json.loads(script.string))
        except json.JSONDecodeError:
            continue
            
    # Check for Bot-Friendliness
    robots_meta = soup.find('meta', attrs={'name': 'robots'})
    is_bot_friendly = True
    robots_content = robots_meta.get('content', '').lower() if robots_meta else "index, follow"
    if 'noindex' in robots_content:
        is_bot_friendly = False
        
    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "h1_count": len(h1_tags),
        "h1_samples": h1_tags[:3],
        "h2_count": len(h2_tags),
        "json_ld_schemas_count": len(schema_data),
        "schemas": schema_data[:2], # Send up to 2 schemas to AI to save token context limits
        "bot_friendly": is_bot_friendly,
        "robots_directive": robots_content,
        "canonical_url": canonical_url,
        "og_title": og_title,
        "og_description": og_desc,
        "word_count": word_count
    }

def analyze_with_ai(api_key, page_data):
    """Uses Gemini 1.5 Flash to run the Discovery Health Audit."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a Senior Technical SEO and Answer Engine Optimization (AEO) expert.
    Analyze the following extracted web page data to determine how likely AI agents 
    (like Perplexity, Search Generative Experience, or ChatGPT) are to understand and cite this page.
    
    Page Data:
    {json.dumps(page_data, indent=2)}
    
    Based on this data, provide an audit with the following JSON structure exactly. 
    Do not output any markdown code blocks (e.g., ```json). Return ONLY valid JSON:
    {{
        "aeo_score": <An integer from 0 to 100 based on the clarity, schema richness, and entity definition>,
        "schema_validation": "<A short string explaining if the JSON-LD is valid and rich enough for AI reasoning>",
        "gap_analysis": "<A string explaining what is missing that would prevent an AI from recommending this>",
        "pm_action_plan": [
            "<Action item 1>",
            "<Action item 2>",
            "<Action item 3>"
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up in case the model returns markdown code block anyway
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        return {"error": f"AI Audit failed: {str(e)}"}

def generate_signal_map(data):
    """Generate signal map boolean values."""
    signals = {
        "Page Title": bool(data.get('title')),
        "Meta Description": bool(data.get('meta_description')),
        "Canonical URL": bool(data.get('canonical_url')),
        "H1 Header": data.get('h1_count', 0) > 0,
        "H2 Headers": data.get('h2_count', 0) > 0,
        "Open Graph Tags": bool(data.get('og_title') or data.get('og_description')),
        "Substantive Content (>300 words)": data.get('word_count', 0) > 300,
        "JSON-LD Schema": data.get('json_ld_schemas_count', 0) > 0,
        "Bot Friendly (Indexable)": data.get('bot_friendly', False)
    }
    return signals

def export_markdown_report(data, audit, title_prefix="AEO & Discovery Audit Report"):
    """Format report into Markdown for export to Jira/Notion."""
    md = f"# {title_prefix}\n\n"
    md += f"**Target URL**: {data.get('url')}\n"
    md += f"**AEO Score**: {audit.get('aeo_score')}/100\n\n"
    
    md += "## Signal Map\n"
    signals = generate_signal_map(data)
    for k, v in signals.items():
        md += f"- {'✅' if v else '❌'} {k}\n"
        
    md += "\n## Schema Validation\n"
    md += f"{audit.get('schema_validation')}\n\n"
    
    md += "## Gap Analysis\n"
    md += f"{audit.get('gap_analysis')}\n\n"
    
    md += "## PM Action Plan\n"
    for i, act in enumerate(audit.get('pm_action_plan', [])):
        md += f"{i+1}. {act}\n"
        
    return md

# === UI Layout ===
st.markdown('<div class="main-header">AnswerSignal 📡</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The AEO & Discovery Auditor for AI Search Engines</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key to run the audit.")
    if not api_key:
        st.warning("Please provide a Gemini API Key to enable AI analysis.")

    st.markdown("---")
    st.markdown("""
    **What is this?**  
    AnswerSignal evaluates how well your webpage is optimized for Answer Engines like Perplexity, ChatGPT, and Google SGE. 
    It checks technical SEO signals, schema markup, and entity definitions.
    """)

# Main Content
col1, col2 = st.columns([3, 1])
with col1:
    target_url = st.text_input("Target URL", placeholder="https://example.com")
    
with col2:
    st.write("")
    st.write("")
    compare_mode = st.toggle("Compare vs Competitor")

competitor_url = None
if compare_mode:
    competitor_url = st.text_input("Competitor URL", placeholder="https://competitor.com")

if st.button("Run Audit", type="primary"):
    if not api_key:
        st.error("API Key is required to run the audit.")
        st.stop()
        
    if not target_url or not is_valid_url(target_url):
        st.error("Please enter a valid Target URL.")
        st.stop()
        
    if compare_mode and (not competitor_url or not is_valid_url(competitor_url)):
        st.error("Please enter a valid Competitor URL for comparison.")
        st.stop()
        
    with st.spinner("Extracting signals & analyzing with Gemini..."):
        # Process Target
        data_target = extract_aeo_signals(target_url)
        if "error" in data_target:
            st.error(data_target["error"])
            st.stop()
            
        audit_target = analyze_with_ai(api_key, data_target)
        if "error" in audit_target:
            st.error(audit_target["error"])
            st.stop()
            
        # Process Competitor if enabled
        data_comp = None
        audit_comp = None
        if compare_mode:
            data_comp = extract_aeo_signals(competitor_url)
            if "error" in data_comp:
                st.warning(f"Could not fetch competitor URL ({competitor_url}). The site might be blocking bots. Details: {data_comp['error']}")
            else:
                audit_comp = analyze_with_ai(api_key, data_comp)
                if "error" in audit_comp:
                    st.warning(f"Failed to analyze competitor URL: {audit_comp['error']}")
        
        st.success("Audit Complete!")
        
        # Display Results
        if compare_mode and audit_comp and "error" not in audit_comp:
            # Comparison View
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Your Page")
                st.metric("AEO Citability Score", f"{audit_target.get('aeo_score', 0)}/100")
                st.progress(audit_target.get('aeo_score', 0) / 100)
                
            with c2:
                st.subheader("Competitor Page")
                st.metric("AEO Citability Score", f"{audit_comp.get('aeo_score', 0)}/100")
                st.progress(audit_comp.get('aeo_score', 0) / 100)
                
            st.divider()
            
            # Side-by-side Signal Map
            st.subheader("Signal Map Comparison")
            sig_target = generate_signal_map(data_target)
            sig_comp = generate_signal_map(data_comp)
            
            df_signals = pd.DataFrame({
                "Signal": list(sig_target.keys()),
                "Your Page": [("✅" if v else "❌") for v in sig_target.values()],
                "Competitor": [("✅" if v else "❌") for v in sig_comp.values()]
            })
            st.dataframe(df_signals, hide_index=True, use_container_width=True)
            
            st.divider()
            
            st.subheader("Insights (Your Page)")
            st.write("**Schema Validation:**", audit_target.get("schema_validation"))
            st.write("**Gap Analysis:**", audit_target.get("gap_analysis"))
            st.write("**Action Plan:**")
            for act in audit_target.get("pm_action_plan", []):
                st.markdown(f"- {act}")
                
            st.subheader("Insights (Competitor)")
            st.write("**Schema Validation:**", audit_comp.get("schema_validation"))
            st.write("**Gap Analysis:**", audit_comp.get("gap_analysis"))
            
            md_export = export_markdown_report(data_target, audit_target, title_prefix="AEO Audit (Vs. Competitor)")
            
        else:
            # Single View
            st.subheader("AEO Citability Score")
            score = audit_target.get('aeo_score', 0)
            st.metric(label="", value=f"{score}/100")
            st.progress(score / 100)
            
            st.divider()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Signal Map")
                signals = generate_signal_map(data_target)
                for k, v in signals.items():
                    st.markdown(f"{'✅' if v else '❌'} **{k}**")
            
            with col_b:
                st.subheader("Schema & Gap Analysis")
                st.markdown(f"**Schema Validation:** {audit_target.get('schema_validation')}")
                st.markdown(f"**Gap Analysis:** {audit_target.get('gap_analysis')}")
            
            st.divider()
            
            st.subheader("PM Action Plan (Top 3 Recommendations)")
            for i, act in enumerate(audit_target.get('pm_action_plan', [])):
                st.info(f"**{i+1}.** {act}")
                
            md_export = export_markdown_report(data_target, audit_target)
            
        st.divider()
        st.download_button(
            label="Export PM Report as Markdown",
            data=md_export,
            file_name="aeo_audit_report.md",
            mime="text/markdown"
        )
