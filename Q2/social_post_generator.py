import re
import json
import time
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import openai  
import requests  

@dataclass
class PlatformConfig:
    name: str
    max_length: int
    style_guidelines: str
    features: List[str]
    optimal_hashtags: Tuple[int, int]  # (min, max)
    tone: str
    
@dataclass
class ContentMetrics:
    character_count: int
    word_count: int
    hashtag_count: int
    engagement_potential: str
    platform_compliance: bool
    additional_metrics: Dict[str, any] = None

@dataclass
class GeneratedPost:
    """Structure for generated social media post"""
    platform: str
    content: str
    metrics: ContentMetrics
    timestamp: str
    
@dataclass
class BlogAnalysis:
    """Analysis results from blog content"""
    title: str
    key_points: List[str]
    word_count: int
    main_topics: List[str]
    tone: str
    target_audience: str

class PlatformManager:
    """Manages platform configurations and requirements"""
    
    def __init__(self):
        self.platforms = {
            'twitter': PlatformConfig(
                name='Twitter/X',
                max_length=280,
                style_guidelines='conversational, trending hashtags, call-to-action',
                features=['hashtags', 'mentions', 'threads', 'polls'],
                optimal_hashtags=(2, 3),
                tone='casual, engaging'
            ),
            'linkedin': PlatformConfig(
                name='LinkedIn',
                max_length=3000,
                style_guidelines='professional, industry insights, networking',
                features=['professional tone', 'industry hashtags', 'thought leadership'],
                optimal_hashtags=(3, 5),
                tone='professional, authoritative'
            ),
            'instagram': PlatformConfig(
                name='Instagram',
                max_length=2200,
                style_guidelines='visual storytelling, lifestyle, engaging captions',
                features=['emojis', 'story-driven', 'visual cues', 'user-generated content'],
                optimal_hashtags=(5, 10),
                tone='visual, lifestyle-focused'
            ),
            'facebook': PlatformConfig(
                name='Facebook',
                max_length=63206,
                style_guidelines='community-focused, detailed, conversational',
                features=['community building', 'detailed posts', 'engagement', 'sharing'],
                optimal_hashtags=(1, 3),
                tone='conversational, community-oriented'
            ),
            'tiktok': PlatformConfig(
                name='TikTok',
                max_length=300,
                style_guidelines='trendy, energetic, video-first content',
                features=['trending sounds', 'challenges', 'youth appeal', 'viral elements'],
                optimal_hashtags=(3, 8),
                tone='trendy, energetic'
            )
        }
    
    def get_platform_config(self, platform: str) -> Optional[PlatformConfig]:
        return self.platforms.get(platform.lower())
    
    def get_all_platforms(self) -> List[str]:
        return list(self.platforms.keys())

class ContentAnalyzer:
    """Analyzes blog content to extract key information"""
    
    def analyze_blog_content(self, content: str) -> BlogAnalysis:
        """Extract key information from blog content"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Extract title (first heading or first line)
        title = self._extract_title(lines)
        
        # Extract key points (headings, bullet points)
        key_points = self._extract_key_points(lines)
        
        # Basic metrics
        words = content.split()
        word_count = len(words)
        
        # Extract main topics (simplified - could use NLP libraries)
        main_topics = self._extract_topics(content)
        
        # Analyze tone (simplified)
        tone = self._analyze_tone(content)
        
        # Determine target audience (simplified)
        target_audience = self._determine_audience(content)
        
        return BlogAnalysis(
            title=title,
            key_points=key_points[:5],  # Top 5 key points
            word_count=word_count,
            main_topics=main_topics,
            tone=tone,
            target_audience=target_audience
        )
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract title from content"""
        for line in lines:
            if line.startswith('#'):
                return re.sub(r'^#+\s*', '', line)
        return lines[0] if lines else "Blog Post"
    
    def _extract_key_points(self, lines: List[str]) -> List[str]:
        """Extract key points from headings and structure"""
        key_points = []
        
        for line in lines:
            # Headings
            if re.match(r'^#+\s+', line):
                key_points.append(re.sub(r'^#+\s*', '', line))
            # Numbered points
            elif re.match(r'^\d+\.\s+', line):
                key_points.append(re.sub(r'^\d+\.\s*', '', line))
            # Bullet points
            elif re.match(r'^[-*]\s+', line):
                key_points.append(re.sub(r'^[-*]\s*', '', line))
        
        return key_points
    
    def _extract_topics(self, content: str) -> List[str]:
        """Simple topic extraction (could be enhanced with NLP)"""
        # Common business/tech topics
        topic_keywords = {
            'technology': ['tech', 'digital', 'AI', 'software', 'data', 'automation'],
            'business': ['business', 'strategy', 'growth', 'revenue', 'market'],
            'productivity': ['productivity', 'efficiency', 'workflow', 'optimization'],
            'remote work': ['remote', 'work from home', 'distributed', 'virtual'],
            'marketing': ['marketing', 'brand', 'customer', 'audience', 'campaign']
        }
        
        content_lower = content.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Return top 3 topics
    
    def _analyze_tone(self, content: str) -> str:
        """Simple tone analysis"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['exciting', 'amazing', 'incredible', '!']):
            return 'enthusiastic'
        elif any(word in content_lower for word in ['professional', 'industry', 'strategic']):
            return 'professional'
        elif any(word in content_lower for word in ['tips', 'how to', 'guide', 'tutorial']):
            return 'educational'
        else:
            return 'informative'
    
    def _determine_audience(self, content: str) -> str:
        """Determine target audience"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['business', 'professional', 'enterprise']):
            return 'professionals'
        elif any(word in content_lower for word in ['startup', 'entrepreneur', 'founder']):
            return 'entrepreneurs'
        elif any(word in content_lower for word in ['developer', 'code', 'programming']):
            return 'developers'
        else:
            return 'general audience'

class PromptEngine:
    """Generates platform-specific prompts for LLM"""
    
    def __init__(self, platform_manager: PlatformManager):
        self.platform_manager = platform_manager
    
    def generate_prompt(self, analysis: BlogAnalysis, platform: str) -> str:
        """Generate platform-specific prompt for LLM"""
        config = self.platform_manager.get_platform_config(platform)
        if not config:
            raise ValueError(f"Unknown platform: {platform}")
        
        base_context = f"""
Blog Article Analysis:
- Title: {analysis.title}
- Key Points: {', '.join(analysis.key_points)}
- Main Topics: {', '.join(analysis.main_topics)}
- Tone: {analysis.tone}
- Target Audience: {analysis.target_audience}
- Word Count: {analysis.word_count}
        """
        
        platform_prompts = {
            'twitter': self._twitter_prompt(config, base_context),
            'linkedin': self._linkedin_prompt(config, base_context),
            'instagram': self._instagram_prompt(config, base_context),
            'facebook': self._facebook_prompt(config, base_context),
            'tiktok': self._tiktok_prompt(config, base_context)
        }
        
        return platform_prompts.get(platform, self._generic_prompt(config, base_context))
    
    def _twitter_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create a Twitter/X post that:
- Stays under {config.max_length} characters
- Uses {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]} relevant hashtags
- Has a conversational, engaging tone
- Includes a call-to-action or question to spark engagement
- Could potentially go viral or get retweeted
- Fits the platform's fast-paced, news-focused environment

Style: {config.style_guidelines}
"""
    
    def _linkedin_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create a LinkedIn post that:
- Maintains a professional, thought-leadership tone
- Is 150-300 words long (optimal for LinkedIn engagement)
- Includes {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]} industry-relevant hashtags
- Positions the author as an expert in their field
- Encourages professional networking and meaningful discussion
- Could include a personal insight or professional experience
- Appeals to business professionals and decision-makers

Style: {config.style_guidelines}
"""
    
    def _instagram_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create an Instagram caption that:
- Uses storytelling and visual language (assumes accompanying image/video)
- Includes relevant emojis naturally throughout the text
- Is engaging and lifestyle-focused while maintaining value
- Uses {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]} strategic hashtags
- Encourages engagement (likes, comments, saves, shares)
- Appeals to visual learners and lifestyle-conscious audience
- Could work with carousel posts, reels, or single images

Style: {config.style_guidelines}
"""
    
    def _facebook_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create a Facebook post that:
- Is conversational and community-focused
- Can be longer format (100-200 words) to encourage discussion
- Uses a friendly, accessible tone
- Encourages discussion, sharing, and community engagement
- Could include a personal anecdote or relatable story
- Appeals to diverse age groups and communities
- Promotes engagement within Facebook groups and communities

Style: {config.style_guidelines}
"""
    
    def _tiktok_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create TikTok content description that:
- Is short, punchy, and trend-aware
- Uses current internet slang and energetic language
- Focuses on hooks and viral potential
- Includes {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]} trending hashtags
- Appeals to younger demographics (Gen Z/Millennial)
- Suggests accompanying video content ideas
- Could work with trending sounds or challenges

Style: {config.style_guidelines}
"""
    
    def _generic_prompt(self, config: PlatformConfig, context: str) -> str:
        return f"""{context}

Create a {config.name} post that:
- Follows platform guidelines: {config.style_guidelines}
- Stays within {config.max_length} character limit
- Uses appropriate tone: {config.tone}
- Incorporates platform features: {', '.join(config.features)}
- Uses {config.optimal_hashtags[0]}-{config.optimal_hashtags[1]} relevant hashtags
"""

class LLMService:
    """Service for interacting with Language Models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if api_key:
            openai.api_key = api_key
            self.client = openai
    
    async def generate_content(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate content using LLM (with fallback simulation)"""
        if self.client and self.api_key:
            return await self._call_openai_api(prompt, max_tokens)
        else:
            return await self._simulate_llm_response(prompt)
    
    async def _call_openai_api(self, prompt: str, max_tokens: int) -> str:
        """Make actual API call to OpenAI"""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media expert specializing in platform-specific content creation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API call failed: {e}")
            return await self._simulate_llm_response(prompt)
    
    async def _simulate_llm_response(self, prompt: str) -> str:
        """Simulate LLM response for testing purposes"""
        # Add realistic delay
        await asyncio.sleep(1 + (time.time() % 2))
        
        # Extract platform from prompt
        platform = self._extract_platform_from_prompt(prompt)
        
        # Return platform-specific simulated responses
        responses = {
            'twitter': """🚀 Remote work isn't just surviving—it's THRIVING! 

The future workplace is hybrid, results-focused, and puts mental health first. Companies investing in home office setups and digital culture are winning the talent war.

What's your take on the remote work revolution? 

#RemoteWork #FutureOfWork #DigitalTransformation""",
            
            'linkedin': """The Remote Work Revolution: 5 Game-Changing Trends 🌟

Having led distributed teams for 3 years, I've witnessed firsthand how remote work has evolved from emergency response to strategic advantage.

The companies thriving today aren't just allowing remote work—they're mastering it:

✅ Hybrid models that attract top talent
✅ Digital-first cultures that build stronger connections
✅ Results-oriented metrics that boost productivity
✅ Home office investments that show employee value
✅ Mental health prioritization that prevents burnout

The future isn't remote vs. in-office. It's about creating systems that empower people to excel wherever they work.

What trends are you seeing in your industry?

#RemoteWork #FutureOfWork #Leadership #WorkplaceTrends #DigitalTransformation""",
            
            'instagram': """✨ Plot twist: Remote work made us MORE connected, not less 🏠💻

Remember when we thought working from home meant isolation? Yeah... that aged poorly 😅

The companies crushing it right now are the ones who figured out that flexibility isn't a perk—it's THE competitive advantage 🎯

From virtual coffee dates ☕ to home office glow-ups 🪴, we're literally reshaping what work means. And honestly? I'm here for it 💪

The future is hybrid, results-focused, and puts your mental health first. Period. 🔥

What's your remote work game-changer been? Drop it below! ⬇️

#RemoteWork #WorkFromHome #FutureOfWork #DigitalNomad #WorkLifeBalance #MentalHealthMatters #Productivity #HomeOffice #FlexibleWork #WorkplaceTrends""",
            
            'facebook': """🤔 Remember when "working from home" was considered a luxury few could afford?

Fast forward to today, and remote work has become one of the most significant workplace shifts in modern history. But here's what's really interesting—it's not just about location anymore.

The companies that are absolutely crushing it right now have figured out something crucial: remote work success isn't about replicating the office experience online. It's about building something entirely new.

I've been tracking these trends, and here's what's really exciting me:

🏠 Hybrid models aren't compromises—they're upgrades
📊 We're finally measuring what matters (results, not hours)
💡 Digital cultures are often stronger than traditional ones
🎯 Mental health conversations have reached a tipping point

The best part? This isn't just about survival anymore. Companies are thriving because they've embraced flexibility as their secret weapon for attracting incredible talent.

What's been your biggest remote work revelation? I'd love to hear how this shift has impacted your work life!""",
            
            'tiktok': """POV: You're explaining remote work trends to your 2019 self 💀

2019 Me: "Working from home sounds lonely"
2025 Me: "Bestie, we're having virtual coffee dates and building stronger team bonds than ever" ✨

Plot twist: The companies winning rn aren't forcing people back to the office—they're investing in sick home office setups and actually caring about mental health 🔥

No cap, results > hours worked is the energy we needed all along 💯

#RemoteWork #WorkFromHome #PlotTwist #FutureOfWork #MentalHealthCheck #ProductivityHacks #WorkplaceTrends #DigitalNomad #FlexibleWork #TechTok"""
        }
        
        return responses.get(platform, responses['twitter'])
    
    def _extract_platform_from_prompt(self, prompt: str) -> str:
        """Extract platform name from prompt"""
        prompt_lower = prompt.lower()
        platforms = ['twitter', 'linkedin', 'instagram', 'facebook', 'tiktok']
        
        for platform in platforms:
            if platform in prompt_lower:
                return platform
        return 'twitter'  # default

class ContentMetricsAnalyzer:
    """Analyzes generated content for metrics and compliance"""
    
    def __init__(self, platform_manager: PlatformManager):
        self.platform_manager = platform_manager
    
    def analyze_content(self, content: str, platform: str) -> ContentMetrics:
        """Analyze generated content for metrics"""
        config = self.platform_manager.get_platform_config(platform)
        
        # Basic metrics
        char_count = len(content)
        word_count = len(content.split())
        hashtag_count = len(re.findall(r'#\w+', content))
        
        # Platform compliance
        compliance = char_count <= config.max_length
        
        # Engagement potential (simplified scoring)
        engagement_score = self._calculate_engagement_potential(content, platform)
        
        # Additional platform-specific metrics
        additional_metrics = self._get_platform_specific_metrics(content, platform)
        
        return ContentMetrics(
            character_count=char_count,
            word_count=word_count,
            hashtag_count=hashtag_count,
            engagement_potential=engagement_score,
            platform_compliance=compliance,
            additional_metrics=additional_metrics
        )
    
    def _calculate_engagement_potential(self, content: str, platform: str) -> str:
        """Calculate engagement potential based on content features"""
        score = 0
        content_lower = content.lower()
        
        # Question marks increase engagement
        score += content.count('?') * 10
        
        # Call-to-action phrases
        cta_phrases = ['comment', 'share', 'like', 'what do you think', 'let me know', 'drop', 'tag']
        score += sum(5 for phrase in cta_phrases if phrase in content_lower)
        
        # Emojis (for visual platforms)
        if platform in ['instagram', 'tiktok', 'facebook']:
            # Simplified emoji detection
            score += len(re.findall(r'[😀-🿿]|[🌀-🗿]|[🚀-🛿]', content)) * 2
        
        # Hashtags
        hashtag_count = len(re.findall(r'#\w+', content))
        config = self.platform_manager.get_platform_config(platform)
        if config.optimal_hashtags[0] <= hashtag_count <= config.optimal_hashtags[1]:
            score += 15
        
        # Convert score to category
        if score >= 40:
            return "Very High"
        elif score >= 25:
            return "High"
        elif score >= 15:
            return "Medium"
        else:
            return "Low"
    
    def _get_platform_specific_metrics(self, content: str, platform: str) -> Dict[str, any]:
        """Get additional platform-specific metrics"""
        metrics = {}
        
        if platform == 'twitter':
            metrics['thread_potential'] = len(content) > 200
            metrics['retweet_potential'] = '?' in content or 'RT' in content.upper()
        
        elif platform == 'linkedin':
            metrics['professional_tone'] = any(word in content.lower() for word in ['professional', 'industry', 'business', 'strategy'])
            metrics['thought_leadership'] = any(word in content.lower() for word in ['insight', 'trend', 'future', 'innovation'])
        
        elif platform == 'instagram':
            metrics['emoji_count'] = len(re.findall(r'[😀-🿿]|[🌀-🗿]|[🚀-🛿]', content))
            metrics['visual_language'] = any(word in content.lower() for word in ['see', 'look', 'visual', 'image', 'picture'])
        
        elif platform == 'facebook':
            metrics['discussion_potential'] = content.count('?') + content.lower().count('what do you think')
            metrics['share_potential'] = any(word in content.lower() for word in ['share', 'spread', 'tell others'])
        
        elif platform == 'tiktok':
            metrics['trend_potential'] = any(word in content.lower() for word in ['trending', 'viral', 'challenge', 'pov'])
            metrics['youth_appeal'] = any(word in content.lower() for word in ['bestie', 'no cap', 'fr', 'periodt'])
        
        return metrics

class SocialMediaGenerator:
    """Main class that orchestrates the social media content generation"""
    
    def __init__(self, llm_api_key: Optional[str] = None):
        self.platform_manager = PlatformManager()
        self.content_analyzer = ContentAnalyzer()
        self.prompt_engine = PromptEngine(self.platform_manager)
        self.llm_service = LLMService(llm_api_key)
        self.metrics_analyzer = ContentMetricsAnalyzer(self.platform_manager)
        self.generation_history = []
    
    async def generate_posts(self, blog_content: str, target_platforms: List[str] = None) -> Dict[str, GeneratedPost]:
        """Generate social media posts for specified platforms"""
        if target_platforms is None:
            target_platforms = self.platform_manager.get_all_platforms()
        
        # Analyze blog content
        analysis = self.content_analyzer.analyze_blog_content(blog_content)
        
        # Generate posts for each platform
        generated_posts = {}
        
        for platform in target_platforms:
            try:
                # Generate platform-specific prompt
                prompt = self.prompt_engine.generate_prompt(analysis, platform)
                
                # Generate content using LLM
                content = await self.llm_service.generate_content(prompt)
                
                # Analyze generated content
                metrics = self.metrics_analyzer.analyze_content(content, platform)
                
                # Create post object
                post = GeneratedPost(
                    platform=platform,
                    content=content,
                    metrics=metrics,
                    timestamp=datetime.now().isoformat()
                )
                
                generated_posts[platform] = post
                
            except Exception as e:
                print(f"Failed to generate content for {platform}: {e}")
                continue
        
        # Save to history
        self.generation_history.append({
            'timestamp': datetime.now().isoformat(),
            'blog_analysis': asdict(analysis),
            'generated_posts': {k: asdict(v) for k, v in generated_posts.items()}
        })
        
        return generated_posts
    
    def export_posts(self, posts: Dict[str, GeneratedPost], filename: str = None) -> str:
        """Export generated posts to JSON file"""
        if filename is None:
            filename = f"social_media_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'posts': {k: asdict(v) for k, v in posts.items()}
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def get_platform_info(self) -> Dict[str, dict]:
        """Get information about all supported platforms"""
        return {k: asdict(v) for k, v in self.platform_manager.platforms.items()}

# ===== Example Usage =====
async def main():
    """Example usage of the Social Media Generator"""
    
    # Sample blog content
    sample_blog = """# The Future of Remote Work: 5 Trends Reshaping the Workplace

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
    
    # Initialize generator (without API key for demo)
    generator = SocialMediaGenerator()
    
    # Generate posts for all platforms
    print("Generating social media posts...")
    posts = await generator.generate_posts(sample_blog)
    
    # Display results
    for platform, post in posts.items():
        print(f"\n{'='*50}")
        print(f"PLATFORM: {platform.upper()}")
        print(f"{'='*50}")
        print(post.content)
        print(f"\nMetrics:")
        print(f"- Characters: {post.metrics.character_count}")
        print(f"- Words: {post.metrics.word_count}")
        print(f"- Hashtags: {post.metrics.hashtag_count}")
        print(f"- Engagement Potential: {post.metrics.engagement_potential}")
        print(f"- Platform Compliant: {post.metrics.platform_compliance}")
        
        if post.metrics.additional_metrics:
            print(f"- Additional: {post.metrics.additional_metrics}")
    
    # Export results
    filename = generator.export_posts(posts)
    print(f"\nResults exported to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())