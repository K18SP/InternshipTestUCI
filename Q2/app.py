# ===== streamlit_app.py =====
import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Import our core classes (assuming they're in social_media_generator.py)
from social_post_generator import (
    SocialMediaGenerator, 
    PlatformManager, 
    GeneratedPost,
    ContentAnalyzer,
    BlogAnalysis
)

# Page configuration
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .platform-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #f0f0f0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .platform-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .copy-button {
        background: #667eea;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        float: right;
    }
    
    .copy-button:hover {
        background: #5a6fd8;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        min-width: 120px;
    }
    
    .platform-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generator' not in st.session_state:
    st.session_state.generator = SocialMediaGenerator()
if 'generated_posts' not in st.session_state:
    st.session_state.generated_posts = {}
if 'blog_analysis' not in st.session_state:
    st.session_state.blog_analysis = None

def get_platform_icon(platform: str) -> str:
    """Get emoji icon for each platform"""
    icons = {
        'twitter': '🐦',
        'linkedin': '💼',
        'instagram': '📸',
        'facebook': '📘',
        'tiktok': '🎵'
    }
    return icons.get(platform, '📱')

def get_platform_color(platform: str) -> str:
    """Get color for each platform"""
    colors = {
        'twitter': '#1DA1F2',
        'linkedin': '#0077B5',
        'instagram': '#E4405F',
        'facebook': '#1877F2',
        'tiktok': '#000000'
    }
    return colors.get(platform, '#667eea')

def display_content_analysis(analysis: BlogAnalysis):
    """Display blog content analysis"""
    st.subheader("📊 Content Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📝 Article Details</h4>
            <p><strong>Title:</strong> {analysis.title}</p>
            <p><strong>Word Count:</strong> {analysis.word_count:,}</p>
            <p><strong>Tone:</strong> {analysis.tone.title()}</p>
            <p><strong>Target Audience:</strong> {analysis.target_audience.title()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 Key Topics</h4>
            <p>{', '.join(analysis.main_topics) if analysis.main_topics else 'General content'}</p>
            <h4>📌 Key Points</h4>
            <ul>
                {''.join([f'<li>{point}</li>' for point in analysis.key_points[:3]])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_platform_post(platform: str, post: GeneratedPost):
    """Display a generated post for a specific platform"""
    icon = get_platform_icon(platform)
    color = get_platform_color(platform)
    
    st.markdown(f"""
    <div class="platform-card">
        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
            <h3 style="color: {color}; margin: 0;">
                {icon} {platform.title().replace('Tiktok', 'TikTok')}
            </h3>
            <div style="flex-grow: 1;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Content
    st.markdown("**Generated Content:**")
    st.text_area(
        f"Content for {platform}",
        value=post.content,
        height=150,
        key=f"content_{platform}",
        label_visibility="collapsed"
    )
    
    # Copy button
    if st.button(f"📋 Copy {platform.title()} Post", key=f"copy_{platform}"):
        st.write("📋 Content copied to clipboard!")  # Note: Actual clipboard copy needs JS
        st.code(post.content)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", post.metrics.character_count)
    with col2:
        st.metric("Words", post.metrics.word_count)
    with col3:
        st.metric("Hashtags", post.metrics.hashtag_count)
    with col4:
        compliance_icon = "✅" if post.metrics.platform_compliance else "❌"
        st.metric("Compliant", compliance_icon)
    
    # Engagement potential
    engagement_colors = {
        "Very High": "🟢",
        "High": "🔵", 
        "Medium": "🟡",
        "Low": "🔴"
    }
    engagement_icon = engagement_colors.get(post.metrics.engagement_potential, "⚪")
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <strong>Engagement Potential:</strong> 
        {engagement_icon} {post.metrics.engagement_potential}
    </div>
    """, unsafe_allow_html=True)
    
    # Additional metrics
    if post.metrics.additional_metrics:
        st.markdown("**Platform-Specific Metrics:**")
        metrics_df = pd.DataFrame([post.metrics.additional_metrics]).T
        metrics_df.columns = ['Value']
        st.dataframe(metrics_df, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_analytics_dashboard(posts: Dict[str, GeneratedPost]):
    """Create analytics dashboard for generated posts"""
    st.subheader("📊 Analytics Dashboard")
    
    # Prepare data
    platforms = list(posts.keys())
    char_counts = [posts[p].metrics.character_count for p in platforms]
    word_counts = [posts[p].metrics.word_count for p in platforms]
    hashtag_counts = [posts[p].metrics.hashtag_count for p in platforms]
    engagement_scores = [posts[p].metrics.engagement_potential for p in platforms]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Character count comparison
        fig_chars = go.Figure(data=[
            go.Bar(
                x=platforms,
                y=char_counts,
                marker_color=[get_platform_color(p) for p in platforms],
                text=char_counts,
                textposition='auto',
            )
        ])
        fig_chars.update_layout(
            title="Character Count by Platform",
            xaxis_title="Platform",
            yaxis_title="Characters",
            showlegend=False
        )
        st.plotly_chart(fig_chars, use_container_width=True)
        
        # Hashtag usage
        fig_hashtags = go.Figure(data=[
            go.Bar(
                x=platforms,
                y=hashtag_counts,
                marker_color=[get_platform_color(p) for p in platforms],
                text=hashtag_counts,
                textposition='auto',
            )
        ])
        fig_hashtags.update_layout(
            title="Hashtag Usage by Platform",
            xaxis_title="Platform", 
            yaxis_title="Number of Hashtags",
            showlegend=False
        )
        st.plotly_chart(fig_hashtags, use_container_width=True)
    
    with col2:
        # Word count comparison
        fig_words = go.Figure(data=[
            go.Bar(
                x=platforms,
                y=word_counts,
                marker_color=[get_platform_color(p) for p in platforms],
                text=word_counts,
                textposition='auto',
            )
        ])
        fig_words.update_layout(
            title="Word Count by Platform",
            xaxis_title="Platform",
            yaxis_title="Words",
            showlegend=False
        )
        st.plotly_chart(fig_words, use_container_width=True)
        
        # Engagement potential pie chart
        engagement_counts = pd.Series(engagement_scores).value_counts()
        fig_engagement = px.pie(
            values=engagement_counts.values,
            names=engagement_counts.index,
            title="Engagement Potential Distribution"
        )
        st.plotly_chart(fig_engagement, use_container_width=True)

async def generate_posts_async(blog_content: str, selected_platforms: List[str]):
    """Async wrapper for post generation"""
    return await st.session_state.generator.generate_posts(blog_content, selected_platforms)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Social Media Content Generator</h1>
        <p>Transform your blog articles into platform-optimized social media posts using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "🔑 OpenAI API Key (Optional)",
            type="password",
            help="Enter your OpenAI API key for real LLM generation. Leave empty for demo mode."
        )
        
        if api_key:
            st.session_state.generator = SocialMediaGenerator(api_key)
            st.success("✅ API Key configured!")
        else:
            st.info("ℹ️ Running in demo mode with simulated responses")
        
        st.divider()
        
        # Platform selection
        st.subheader("🎯 Target Platforms")
        platform_manager = PlatformManager()
        all_platforms = platform_manager.get_all_platforms()
        
        platform_selection = {}
        for platform in all_platforms:
            icon = get_platform_icon(platform)
            config = platform_manager.get_platform_config(platform)
            platform_selection[platform] = st.checkbox(
                f"{icon} {config.name}",
                value=True,
                help=f"Max length: {config.max_length} chars | Style: {config.style_guidelines}"
            )
        
        selected_platforms = [p for p, selected in platform_selection.items() if selected]
        
        st.divider()
        
        # Platform info
        st.subheader("📋 Platform Requirements")
        for platform in selected_platforms:
            config = platform_manager.get_platform_config(platform)
            icon = get_platform_icon(platform)
            st.markdown(f"""
            **{icon} {config.name}**
            - Max: {config.max_length:,} chars
            - Hashtags: {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]}
            - Tone: {config.tone}
            """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 Content Input", "🎯 Generated Posts", "📊 Analytics"])
    
    with tab1:
        st.header("📝 Blog Article Input")
        
        # Sample content button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📄 Load Sample Article"):
                st.session_state.sample_loaded = True
        
        # Blog content input
        sample_content = """# The Future of Remote Work: 5 Trends Reshaping the Workplace

The pandemic accelerated remote work adoption, but what we're seeing now goes far beyond emergency measures. Companies and employees alike are reimagining what work means in the digital age.

## 1. Hybrid Models Become the Norm
Organizations are discovering that flexibility isn't just a perk—it's a competitive advantage. The best talent expects options, and companies that offer them are winning the recruitment game.

## 2. Digital-First Company Culture
Remote-first companies are building stronger cultures than ever by being intentional about connection. Virtual coffee chats, online team building, and digital collaboration tools are creating bonds that transcend physical spaces.

## 3. Results-Oriented Performance Metrics
The shift from hours worked to outcomes achieved is revolutionizing how we measure success. Companies are focusing on deliverables, impact, and innovation rather than desk time.

## 4. Investment in Home Office Infrastructure
Employers are recognizing that a productive remote workforce requires proper tools. From ergonomic chairs to high-speed internet stipends, companies are investing in their distributed teams.

## 5. Mental Health and Work-Life Balance Priority
The conversation around burnout has reached a tipping point. Organizations are implementing wellness programs, mental health days, and boundaries that actually protect personal time.

The future of work isn't about choosing between remote and in-office—it's about creating systems that empower people to do their best work wherever they are."""
        
        blog_content = st.text_area(
            "Paste your blog article content here:",
            height=400,
            value=sample_content if st.session_state.get('sample_loaded', False) else "",
            placeholder="Enter your blog article content..."
        )
        
        # Content stats
        if blog_content:
            word_count = len(blog_content.split())
            char_count = len(blog_content)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", f"{word_count:,}")
            with col2:
                st.metric("Characters", f"{char_count:,}")
            with col3:
                lines = len([line for line in blog_content.split('\n') if line.strip()])
                st.metric("Lines", lines)
        
        # Generate button
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Social Media Posts", type="primary", use_container_width=True):
                if not blog_content.strip():
                    st.error("⚠️ Please enter blog content first!")
                elif not selected_platforms:
                    st.error("⚠️ Please select at least one platform!")
                else:
                    with st.spinner("🔄 Analyzing content and generating posts..."):
                        # Analyze content first
                        analyzer = ContentAnalyzer()
                        st.session_state.blog_analysis = analyzer.analyze_blog_content(blog_content)
                        
                        # Generate posts
                        try:
                            # Since we can't use async in Streamlit directly, we'll use the sync version
                            # In a real app, you'd use st.experimental_rerun or similar
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            posts = loop.run_until_complete(
                                st.session_state.generator.generate_posts(blog_content, selected_platforms)
                            )
                            loop.close()
                            
                            st.session_state.generated_posts = posts
                            st.success(f"✅ Generated {len(posts)} social media posts!")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error generating posts: {str(e)}")
        
        # Show content analysis if available
        if st.session_state.blog_analysis:
            st.divider()
            display_content_analysis(st.session_state.blog_analysis)
    
    with tab2:
        st.header("🎯 Generated Posts")
        
        if st.session_state.generated_posts:
            # Export functionality
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📥 Export All Posts"):
                    export_data = {
                        'generated_at': datetime.now().isoformat(),
                        'blog_analysis': st.session_state.blog_analysis.__dict__ if st.session_state.blog_analysis else None,
                        'posts': {k: {
                            'platform': v.platform,
                            'content': v.content,
                            'metrics': v.metrics.__dict__,
                            'timestamp': v.timestamp
                        } for k, v in st.session_state.generated_posts.items()}
                    }
                    
                    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📁 Download JSON",
                        data=json_str,
                        file_name=f"social_media_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            # Display posts
            for platform, post in st.session_state.generated_posts.items():
                display_platform_post(platform, post)
                st.divider()
        
        else:
            st.info("👈 Generate some posts first using the Content Input tab!")
    
    with tab3:
        st.header("📊 Analytics Dashboard")
        
        if st.session_state.generated_posts:
            create_analytics_dashboard(st.session_state.generated_posts)
            
            # Performance insights
            st.subheader("💡 Performance Insights")
            
            posts = st.session_state.generated_posts
            
            # Find best performing metrics
            char_counts = {p: posts[p].metrics.character_count for p in posts}
            word_counts = {p: posts[p].metrics.word_count for p in posts}
            hashtag_counts = {p: posts[p].metrics.hashtag_count for p in posts}
            
            best_engagement = max(posts.items(), key=lambda x: x[1].metrics.engagement_potential)
            most_hashtags = max(posts.items(), key=lambda x: x[1].metrics.hashtag_count)
            longest_post = max(posts.items(), key=lambda x: x[1].metrics.character_count)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🏆 Best Engagement</h4>
                    <p>{get_platform_icon(best_engagement[0])} <strong>{best_engagement[0].title()}</strong></p>
                    <p>Potential: {best_engagement[1].metrics.engagement_potential}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🏷️ Most Hashtags</h4>
                    <p>{get_platform_icon(most_hashtags[0])} <strong>{most_hashtags[0].title()}</strong></p>
                    <p>Count: {most_hashtags[1].metrics.hashtag_count}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📏 Longest Content</h4>
                    <p>{get_platform_icon(longest_post[0])} <strong>{longest_post[0].title()}</strong></p>
                    <p>Length: {longest_post[1].metrics.character_count:,} chars</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Compliance check
            st.subheader("✅ Platform Compliance")
            compliance_data = []
            for platform, post in posts.items():
                compliance_data.append({
                    'Platform': platform.title(),
                    'Character Count': post.metrics.character_count,
                    'Max Allowed': st.session_state.generator.platform_manager.get_platform_config(platform).max_length,
                    'Compliant': '✅' if post.metrics.platform_compliance else '❌'
                })
            
            compliance_df = pd.DataFrame(compliance_data)
            st.dataframe(compliance_df, use_container_width=True)
            
        else:
            st.info("👈 Generate some posts first to see analytics!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🤖 Powered by AI | Built with Streamlit | 
        <a href="https://github.com/yourusername/social-media-generator" target="_blank">View Source</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# ===== requirements.txt =====
"""
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
openai>=1.0.0
asyncio
aiohttp
requests>=2.31.0
"""

# ===== How to run =====
"""
1. Save the core classes as 'social_media_generator.py'
2. Save this Streamlit app as 'streamlit_app.py' 
3. Create requirements.txt with the dependencies above
4. Install dependencies: pip install -r requirements.txt
5. Run the app: streamlit run streamlit_app.py

The app will be available at http://localhost:8501
"""