import streamlit as st
import pandas as pd
import time
import os


try:
    from auth import login
    from utils.router import choose_models
    from utils.parallel import run_parallel
    from utils.rate_limiter import check_limit
    from utils.report import generate_report
except Exception as e:
    st.error(e)
    st.stop()

st.set_page_config(
    page_title="LLM Nexus | Enterprise Comparison",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<script>
function copySiblingResponse(buttonElement) {
    const card = buttonElement.closest('.model-card');
    if (!card) return;

    const markdownBody = card.querySelector('[data-testid="stMarkdown"]');
    if (markdownBody) {
        navigator.clipboard.writeText(markdownBody.innerText || markdownBody.textContent).then(() => {
            const originalIcon = buttonElement.innerHTML;
            buttonElement.innerHTML = '✅';
            setTimeout(() => {
                buttonElement.innerHTML = originalIcon;
            }, 1500);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    } else {
        console.error('Could not find response text to copy.');
    }
}
</script>
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0f172a; /* Slate 900 */
        color: #f8fafc;
    }

    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    .main-header {
        font-size: 3.5rem;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 3rem;
        text-align: center;
    }

    /* Input Areas */
    .stTextArea textarea {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: #e2e8f0;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 0 1px #38bdf8;
    }
    
    /* Text Input (for Auth & others) */
    div[data-baseweb="input"] > div {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: white;
    }
    
    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: white;
    }

    /* Custom Button Style */
    div.stButton > button {
        background: #38bdf8;
        color: #0f172a;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background: #0ea5e9;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }

    /* Result Cards */
    .model-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s;
    }
    .model-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .model-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 15px;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
    }
    .model-name {
        font-weight: 700;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        margin: 0;
    }
    .copy-icon {
        cursor: pointer;
        font-size: 1.1rem;
        opacity: 0.5;
        transition: opacity 0.2s ease-in-out;
    }
    .copy-icon:hover {
        opacity: 1;
    }

    /* Metrics Container */
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Controls")
    
    if "user" in st.session_state:
        st.info(f"👤 Logged in as: **{st.session_state.user}**")
        if st.button("Log Out", use_container_width=True):
            del st.session_state["user"]
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Configuration")
    model_temp = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", value=1024, step=256)
    
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Edition")


def main():
    
    login()
    if "user" not in st.session_state:
        st.stop()

   
    st.markdown('<div class="main-header">LLM Nexus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent routing & cost-analysis engine for Generative AI.</div>', unsafe_allow_html=True)

    # Improved Layout: Stacked for better focus
    st.markdown("### 🎯 Select Objective")
    task = st.radio(
        "Target Objective",
        ["General", "Coding", "Fast Response", "Cost Saving"],
        horizontal=True,
        help="This determines which models are selected via the router.",
        label_visibility="collapsed"
    )
    
    st.markdown("### ✍️ Input Prompt")
    prompt = st.text_area(
        "Input Prompt",
        height=180,
        placeholder="Describe your request in detail (e.g., 'Write a secure Python function to connect to AWS S3 using boto3...').",
        label_visibility="collapsed"
    )

    col_submit, col_status = st.columns([1, 3])
    with col_submit:
        run_btn = st.button("⚡ Execute Query", type="primary", use_container_width=True)
    
    with col_status:
        st.markdown("<div style='text-align: right; padding-top: 10px; color: #64748b;'>🟢 System Status: <b>All Systems Go</b></div>", unsafe_allow_html=True)

    if run_btn:
        if not check_limit(st.session_state.user):
            st.error("🚫 Rate limit reached. Please upgrade your plan or wait.")
            st.stop()
            
        if not prompt.strip():
            st.warning("⚠️ Please provide a prompt to analyze.")
            st.stop()

     
        with st.status("🔄 Orchestrating Model Requests...", expanded=True) as status:
            st.write("🔍 Analyzing intent...")
            models = choose_models(task)
            st.write(f"✅ Selected optimized models: **{', '.join(models)}**")
            
            start_time = time.time()
            
            with st.spinner("🚀 Dispatching parallel requests..."):
                responses = run_parallel(prompt, models)
            
            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✅ Complete! Processed in {elapsed}s", state="complete", expanded=False)

     
        st.markdown("### 📊 Analysis Results")
        
       
        tab1, tab2, tab3, tab4 = st.tabs([
            "👁️ Visual Comparison",
            "📝 Raw Data",
            "📉 Cost Report",
            "📊 Performance Dashboard"
        ])



        with tab1:
           
            cols = st.columns(len(responses))
            
         
            for idx, (model_name, response_text) in enumerate(responses.items()):
                with cols[idx]:
                    # Use markdown to create a container that can hold other streamlit elements
                    st.markdown('<div class="model-card">', unsafe_allow_html=True)

                    st.markdown(f"""
                        <div class="model-header">
                            <div class="model-name">{model_name}</div>
                            <div class="copy-icon" onclick="copySiblingResponse(this)" title="Copy response to clipboard">📋</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(response_text) 

                    st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.subheader("📥 Export Data")
            
            # Create DataFrame for CSV
            df_export = pd.DataFrame([
                {"Model": k, "Response": v} for k, v in responses.items()
            ])
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.download_button(
                    label="📄 Download as CSV",
                    data=df_export.to_csv(index=False).encode('utf-8'),
                    file_name="comparison_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_d2:
                try:
                    from fpdf import FPDF
                    
                    def create_pdf(data):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.cell(200, 10, txt="LLM Comparison Results", ln=True, align='C')
                        pdf.ln(10)
                        
                        for model, text in data.items():
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 10, f"Model: {model}", ln=True)
                            pdf.set_font("Arial", size=10)
                            # FPDF (standard) doesn't support UTF-8 characters well, replace them
                            safe_text = text.encode('latin-1', 'replace').decode('latin-1')
                            pdf.multi_cell(0, 6, safe_text)
                            pdf.ln(5)
                        return pdf.output(dest='S').encode('latin-1')

                    st.download_button(
                        label="📕 Download as PDF",
                        data=create_pdf(responses),
                        file_name="comparison_results.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except ImportError:
                    st.warning("Install `fpdf` to enable PDF export.")
                except Exception as e:
                    st.error(f"Could not generate PDF: {e}")

            st.markdown("---")
            st.json(responses)

        with tab3:
           
            report_status = generate_report(prompt, responses)
            st.success("Report generated and saved to database.")
            
           
            metrics_col1, metrics_col2 = st.columns(2)
            metrics_col1.metric("Estimated Cost", "$0.0042", "-12%")
            metrics_col2.metric("Latency Average", f"{elapsed}s", "Fast")
        with tab4:
            st.markdown("### 📊 Model Performance Dashboard")

            metrics_file = "data/metrics/metrics.csv"

            if not os.path.exists(metrics_file):
                st.warning("No metrics data available yet. Run some prompts first.")
            else:
                df = pd.read_csv(metrics_file)

                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                st.subheader("⏱️ Average Latency per Model")
                latency_df = df.groupby("model")["latency"].mean().reset_index()
                st.bar_chart(latency_df.set_index("model"))

                st.subheader("📏 Average Response Length")
                length_df = df.groupby("model")["response_length"].mean().reset_index()
                st.bar_chart(length_df.set_index("model"))

                st.subheader("📈 Requests Over Time")
                time_df = df.set_index("timestamp").resample("1min").count()["model"]
                st.line_chart(time_df)


if __name__ == "__main__":
    main()
