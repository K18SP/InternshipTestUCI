import streamlit as st
import json
import tempfile
import os
from datetime import datetime
from pdf_checker import analyze_pdf

st.set_page_config(
    page_title="PDF Compliance Analyzer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .upload-section {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📋 PDF Compliance Analyzer</h1>
    <p>Professional Document Analysis & Validation Tool</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Analysis Options")
    analysis_depth = st.selectbox(
        "Analysis Depth",
        ["Standard", "Detailed", "Comprehensive"],
        help="Choose the level of analysis detail"
    )
    
    include_metadata = st.checkbox("Include Metadata Analysis", value=True)
    include_structure = st.checkbox("Include Structure Analysis", value=True)
    include_compliance = st.checkbox("Include Compliance Check", value=True)
    
    st.divider()
    
    st.subheader("📏 Section Page Limits")
    st.info("Configure maximum page limits for specific sections")
    
    use_custom_limits = st.checkbox("Enable Custom Limits")
    
    custom_limits_json = ""
    if use_custom_limits:
        preset_limits = st.selectbox(
            "Use Preset Limits",
            ["None", "Resume Template", "Report Template", "Custom"],
            help="Select a preset or create custom limits"
        )
        
        if preset_limits == "Resume Template":
            custom_limits_json = json.dumps({
                "skills": 2,
                "experience": 3,
                "education": 1,
                "summary": 1
            }, indent=2)
        elif preset_limits == "Report Template":
            custom_limits_json = json.dumps({
                "executive_summary": 2,
                "methodology": 3,
                "results": 5,
                "appendix": 10
            }, indent=2)
        else:
            custom_limits_json = ""
        
        custom_limits = st.text_area(
            "JSON Section Limits",
            value=custom_limits_json,
            height=200,
            help="Define page limits in JSON format",
            placeholder='{\n  "section_name": max_pages,\n  "skills": 2,\n  "experience": 3\n}'
        )
    else:
        custom_limits = ""
    
    max_page_limits = None
    json_valid = True
    if custom_limits.strip() and use_custom_limits:
        try:
            max_page_limits = json.loads(custom_limits)
            st.success(f"✅ Valid JSON ({len(max_page_limits)} sections)")
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")
            json_valid = False

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Document Upload")
    
    # File upload with enhanced UI
    uploaded_file = st.file_uploader(
        "Select PDF Document",
        type=["pdf"],
        help="Upload a PDF file for compliance analysis (Max size: 200MB)"
    )
    
    if uploaded_file:
        # Display file information
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.markdown(f"""
        <div class="status-card">
            <strong>📄 File Information</strong><br>
            <strong>Name:</strong> {uploaded_file.name}<br>
            <strong>Size:</strong> {file_size:.2f} MB<br>
            <strong>Type:</strong> {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("📊 Analysis Summary")
    
    if uploaded_file:
        # Create metrics display
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("File Size", f"{file_size:.1f} MB")
        with col_b:
            st.metric("Status", "Ready", delta="Uploaded")
    else:
        st.info("Upload a PDF to see analysis summary")

# Analysis section
if uploaded_file:
    st.divider()
    
    # Analysis configuration display
    config_cols = st.columns(4)
    with config_cols[0]:
        st.info(f"**Depth:** {analysis_depth}")
    with config_cols[1]:
        st.info(f"**Metadata:** {'✅' if include_metadata else '❌'}")
    with config_cols[2]:
        st.info(f"**Structure:** {'✅' if include_structure else '❌'}")
    with config_cols[3]:
        st.info(f"**Compliance:** {'✅' if include_compliance else '❌'}")
    
    # Analysis button
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        analyze_button = st.button(
            "🔍 Analyze PDF Document",
            use_container_width=True,
            disabled=not json_valid,
            help="Start comprehensive PDF analysis" if json_valid else "Fix JSON errors first"
        )
    
    if analyze_button:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_pdf_path = tmp_file.name
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Initializing analysis...")
            progress_bar.progress(10)
            
            status_text.text("📖 Reading PDF structure...")
            progress_bar.progress(30)
            
            status_text.text("🔍 Performing compliance checks...")
            progress_bar.progress(60)
            
            with st.spinner("Analyzing PDF content..."):
                result = analyze_pdf(temp_pdf_path, max_page_limits=max_page_limits)
            
            status_text.text("✅ Analysis completed successfully!")
            progress_bar.progress(100)
            
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
            
            st.subheader("📋 Analysis Results")
            
            tab1, tab2, tab3 = st.tabs(["📊 Summary", "📄 Detailed Report", "💾 Export"])
            
            with tab1:
                if isinstance(result, dict):
                    summary_cols = st.columns(4)
                    
                    total_pages = result.get('total_pages', 'N/A')
                    
                    def count_failures(data):
                        failures = []
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if value == "fail":
                                    failures.append(key.replace('_', ' ').title())
                                elif isinstance(value, dict):
                                    failures.extend(count_failures(value))
                        return failures
                    
                    failed_items = count_failures(result)
                    issues_found = len(failed_items)
                    
                    def count_passes(data):
                        passes = 0
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if value == "pass":
                                    passes += 1
                                elif isinstance(value, dict):
                                    passes += count_passes(value)
                        return passes
                    
                    passed_items = count_passes(result)
                    total_checks = issues_found + passed_items
                    compliance_score = round((passed_items / total_checks * 100), 1) if total_checks > 0 else 'N/A'
                    
                    with summary_cols[0]:
                        st.metric("Total Pages", total_pages)
                    with summary_cols[1]:
                        st.metric("Compliance Score", f"{compliance_score}%" if isinstance(compliance_score, (int, float)) else compliance_score)
                    with summary_cols[2]:
                        st.metric("Issues Found", issues_found, delta=f"❌ {issues_found}" if issues_found > 0 else "✅ 0")
                    with summary_cols[3]:
                        st.metric("Checks Passed", passed_items, delta=f"✅ {passed_items}")
                
                if failed_items:
                    st.warning(f"⚠️ Found {len(failed_items)} compliance issues requiring attention:")
                    
                    format_fails = []
                    content_fails = []
                    other_fails = []
                    
                    if 'format' in result and isinstance(result['format'], dict):
                        for key, value in result['format'].items():
                            if value == "fail":
                                format_fails.append(key.replace('_', ' ').title())
                    
                    if 'content' in result and isinstance(result['content'], dict):
                        for key, value in result['content'].items():
                            if isinstance(value, str) and value == "fail":
                                content_fails.append(key.replace('_', ' ').title())
                    
                    if format_fails:
                        st.error("📝 **Format Issues:**")
                        for item in format_fails[:5]:
                            st.write(f"• {item}")
                    
                    if content_fails:
                        st.error("📄 **Content Issues:**")
                        for item in content_fails[:5]:
                            st.write(f"• {item}")
                    
                    remaining_issues = len(failed_items) - len(format_fails[:5]) - len(content_fails[:5])
                    if remaining_issues > 0:
                        st.info(f"... and {remaining_issues} more issues. See detailed report for complete analysis.")
                        
                else:
                    st.success("✅ No compliance issues detected! Document meets all requirements.")
            
            with tab2:
                # Detailed JSON report
                st.subheader("Complete Analysis Report")
                
                with st.expander("📋 Full Report Data", expanded=True):
                    st.json(result)
                
                if isinstance(result, dict):
                    if 'format' in result:
                        with st.expander("📝 Format Compliance", expanded=True):
                            format_data = result['format']
                            if isinstance(format_data, dict):
                                col1, col2 = st.columns(2)
                                for i, (key, value) in enumerate(format_data.items()):
                                    display_name = key.replace('_', ' ').title()
                                    status_icon = "✅" if value == "pass" else "❌" if value == "fail" else "ℹ️"
                                    status_color = "success" if value == "pass" else "error" if value == "fail" else "info"
                                    
                                    target_col = col1 if i % 2 == 0 else col2
                                    with target_col:
                                        if value == "pass":
                                            st.success(f"{status_icon} **{display_name}**: Passed")
                                        elif value == "fail":
                                            st.error(f"{status_icon} **{display_name}**: Failed")
                                        else:
                                            st.info(f"{status_icon} **{display_name}**: {value}")
                            else:
                                st.json(format_data)
                    
                    if 'content' in result:
                        with st.expander("📄 Content Analysis", expanded=True):
                            content_data = result['content']
                            if isinstance(content_data, dict):
                                for key, value in content_data.items():
                                    display_name = key.replace('_', ' ').title()
                                    if key.endswith('_pages'):
                                        st.metric(f"{display_name}", value)
                                    else:
                                        status_icon = "✅" if value == "pass" else "❌" if value == "fail" else "ℹ️"
                                        if value == "pass":
                                            st.success(f"{status_icon} **{display_name}**: Compliant")
                                        elif value == "fail":
                                            st.error(f"{status_icon} **{display_name}**: Non-compliant")
                                        else:
                                            st.info(f"**{display_name}**: {value}")
                            else:
                                st.json(content_data)
                    
                    for key, value in result.items():
                        if key not in ['format', 'content']:
                            with st.expander(f"📑 {key.replace('_', ' ').title()}", expanded=False):
                                if isinstance(value, (dict, list)):
                                    st.json(value)
                                else:
                                    st.write(value)
            
            with tab3:
                st.subheader("📥 Export Results")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = uploaded_file.name.rsplit('.', 1)[0]
                
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    json_str = json.dumps(result, indent=2, ensure_ascii=False)
                    st.download_button(
                        "📄 Download JSON Report",
                        json_str,
                        file_name=f"{base_filename}_analysis_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col_export2:
                    summary_text = f"""PDF Compliance Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
File: {uploaded_file.name}
Size: {file_size:.2f} MB

Analysis Configuration:
- Depth: {analysis_depth}
- Metadata Analysis: {'Enabled' if include_metadata else 'Disabled'}
- Structure Analysis: {'Enabled' if include_structure else 'Disabled'}
- Compliance Check: {'Enabled' if include_compliance else 'Disabled'}

Results Summary:
{json.dumps(result, indent=2)}
"""
                    st.download_button(
                        "📝 Download Summary Report",
                        summary_text,
                        file_name=f"{base_filename}_summary_{timestamp}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
        
        finally:
            progress_bar.empty()
            status_text.empty()

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🔐 <strong>Privacy Notice:</strong> Files are processed locally and not stored permanently.</p>
    <p>📧 For support or feedback, contact your system administrator.</p>
</div>
""", unsafe_allow_html=True)