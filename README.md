# AnswerSignal 🤖

**Bridging the gap between traditional SEO and the era of AI-driven discovery.**

---

## 🎯 The Vision: From Search Results to Answers

We are experiencing a fundamental shift in how users find information. The era of scrolling through "10 blue links" is ending. In its place, **Answer Engines** (like Perplexity, ChatGPT, and Google's SGE) synthesize structured information to provide direct, cited answers. 

**The Problem:** AI agents don't click links; they synthesize metadata. If your quality signals are weak, your product is invisible. Traditional SEO tools measure keyword density and backlinks, but they fail to measure *citability* for AI agents.

**AnswerSignal** is the ultimate auditing tool for Product Managers to defend their organic growth strategy. By analyzing your Answer Engine Optimization (AEO) readiness, AnswerSignal scores how likely AI agents are to synthesize, validate, and recommend your product out of the noise.

---

## ✨ Core Features

AnswerSignal acts as a Discovery Health Audit for any public URL, unpacking how robots perceive your content.

*   **💯 AEO Citability Scoring:** A comprehensive 0-100 metric based on entity clarity, semantic richness, and technical bot-friendliness.
*   **📡 Expanded Signal Map:** Checks for critical AEO metadata including Canonical URLs, Open Graph Tags, and Substantive Content.
*   **🔎 JSON-LD Schema Audit:** Automatically extracts and validates your structured data to ensure it's robust enough for AI reasoning.
*   **🥊 Competitive Benchmarking:** Side-by-side URL comparison mode to instantly see how your signaling stacks up against a competitor's.
*   **📋 PM Action Plan:** Generates 3 high-impact, Jira-ready recommendations directly from Gemini's analysis.
*   **📤 One-Click Export:** Instantly export the gap analysis and recommendations as a Markdown file for Jira or Notion.

---

## 📸 Screenshots

*Images coming soon...*

### Main Dashboard
![Main Dashboard](assets/main-dashboard.png)

### Audit Analysis & Signal Map
![Audit Analysis](assets/audit-analysis.png)

### Comparison View
![Comparison View](assets/comparison-view.png)

---

## 🛠️ Tech Stack

AnswerSignal is built for speed and simplicity.

*   **[Python](https://www.python.org/):** Core application logic
*   **[Streamlit](https://streamlit.io/):** Fast, beautiful, dark-mode native web user interface
*   **[Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/flash/):** Highly capable, blazing-fast LLM power for Discovery Health Audits
*   **[BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/):** HTML parsing and AEO signal scraping

---

## 🚀 Installation & Quick Start

Ready to run your first Discovery Audit? Follow these steps to get AnswerSignal running locally:

**1. Clone the repository**
```bash
git clone https://github.com/your-username/AnswerSignal.git
cd AnswerSignal
```

**2. Install requirements**
```bash
pip install -r requirements.txt
```

**3. Run the application**
```bash
streamlit run app.py
```

**4. Run your Audit**
*   Open the local Streamlit URL in your browser.
*   Input your **Google Gemini API Key** in the sidebar.
*   Enter a Target URL and click **Run Audit**.

---

## 👥 Target Audience

AnswerSignal is designed for leaders navigating the modern discovery landscape:

*   **Product Managers:** Ensure feature launches and landing pages are properly surfaced by AI search agents.
*   **Growth Engineers:** Identify and patch metadata leakage that prevents organic AI acquisition.

---
*Built to make the invisible visible.*
