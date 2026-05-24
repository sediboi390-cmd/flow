import sys
import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# --- Output Path (relative to this script, works on any machine) ---
OUTPUT_PATH = Path(__file__).parent / "AI_Tools_Faceless_Channel_Scripts.pdf"

# --- Styles ---
styles = getSampleStyleSheet()

title_style = ParagraphStyle('Title', fontSize=22, textColor=colors.HexColor('#1a1a2e'),
    alignment=TA_CENTER, spaceAfter=6, fontName='Helvetica-Bold')
subtitle_style = ParagraphStyle('Subtitle', fontSize=13, textColor=colors.HexColor('#16213e'),
    alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica')
week_style = ParagraphStyle('Week', fontSize=16, textColor=colors.white,
    backColor=colors.HexColor('#0f3460'), alignment=TA_CENTER, spaceAfter=8,
    spaceBefore=10, fontName='Helvetica-Bold', borderPadding=(6,6,6,6))
video_style = ParagraphStyle('Video', fontSize=13, textColor=colors.white,
    backColor=colors.HexColor('#e94560'), alignment=TA_LEFT, spaceAfter=6,
    spaceBefore=8, fontName='Helvetica-Bold', borderPadding=(5,5,5,5))
scene_style = ParagraphStyle('Scene', fontSize=11, textColor=colors.HexColor('#0f3460'),
    spaceAfter=3, spaceBefore=6, fontName='Helvetica-Bold')
vo_style = ParagraphStyle('VO', fontSize=10, textColor=colors.HexColor('#2d2d2d'),
    spaceAfter=4, fontName='Helvetica-Oblique', leftIndent=10,
    borderPadding=(4,4,4,4), backColor=colors.HexColor('#f0f4ff'))
prompt_label_style = ParagraphStyle('PromptLabel', fontSize=10,
    textColor=colors.HexColor('#e94560'), spaceAfter=2, fontName='Helvetica-Bold')
prompt_style = ParagraphStyle('Prompt', fontSize=9, textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=6, fontName='Courier', leftIndent=10, backColor=colors.HexColor('#f9f9f9'),
    borderPadding=(4,4,4,4))
note_style = ParagraphStyle('Note', fontSize=9, textColor=colors.HexColor('#555555'),
    spaceAfter=4, fontName='Helvetica-Oblique', alignment=TA_CENTER)
body_style = ParagraphStyle('Body', fontSize=10, textColor=colors.HexColor('#333333'),
    spaceAfter=4, fontName='Helvetica', leading=14)



# --- Helper Functions (story passed explicitly — no global side effects) ---
def add_week_header(story, title):
    story.append(Spacer(1, 6))
    story.append(Paragraph(title, week_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 4))

def add_video_header(story, title, day, platform):
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"{day} | {platform}", note_style))
    story.append(Paragraph(f"{title}", video_style))

def add_scene(story, scene_title, voiceover, prompt_text):
    story.append(Paragraph(f"  {scene_title}", scene_style))
    story.append(Paragraph(f"VOICEOVER: {voiceover}", vo_style))
    story.append(Paragraph("SEEDANCE 2 PROMPT:", prompt_label_style))
    story.append(Paragraph(prompt_text.replace('\n', '<br/>'), prompt_style))
    story.append(Spacer(1, 3))


def build_story():
    """Build and return the full PDF story list."""
    story = []

    # ============================================================
    # COVER PAGE
    # ============================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("AI TOOLS FACELESS CHANNEL", title_style))
    story.append(Paragraph("Complete 4-Week Script Collection", subtitle_style))
    story.append(Paragraph("Optimized for Seedance 2 Video Generation", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("YouTube - TikTok - Instagram Reels", note_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This document contains fully scripted voiceovers and Seedance 2 video prompts "
        "for all 12 videos across 4 weeks of content. Each scene includes a ready-to-use "
        "voiceover script and an optimized Seedance 2 prompt using the formula: "
        "[Subject] + [Action] + [Camera Move] + [Style] + [Lighting] + [Audio].",
        body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("CONTENTS", scene_style))
    contents = [
        "WEEK 1 - Launch &amp; Establish (Videos 1-2)",
        "WEEK 2 - Build Audience (Videos 3-5)",
        "WEEK 3 - Monetization Focus (Videos 6-8)",
        "WEEK 4 - Scale &amp; Repeat (Videos 9-12)",
    ]
    for c in contents:
        story.append(Paragraph(f"- {c}", body_style))
    story.append(PageBreak())

    return story


def build_week1(story):
    # ============================================================
    # WEEK 1
    # ============================================================
    add_week_header(story, "WEEK 1 - LAUNCH & ESTABLISH")

    # --- VIDEO 1 ---
    add_video_header(story, "5 AI Tools That Will Replace Your Entire Workflow in 2026", "Day 1", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "What if I told you that 5 free or cheap AI tools could replace a $5,000/month team? Stay until the end -- because number 5 is going to blow your mind.",
        "A futuristic holographic dashboard explodes into view, glowing neon-blue data streams and AI interface panels floating in dark space, dramatic push-in camera move from far to close, cinematic sci-fi style, deep contrast lighting, ambient electronic hum with subtle whoosh sound, 8K sharp, 5 seconds")
    add_scene(story, "SCENE 2 - INTRO",
        "AI is moving so fast that most people are still sleeping on tools that could save them 20 hours a week. Here are the top 5 AI tools changing the game in 2026.",
        "A sleek modern workspace with multiple glowing screens displaying AI dashboards, time-lapse of digital data flowing rapidly across monitors, slow dolly-in camera move, clean corporate tech aesthetic, cool blue ambient lighting with warm accent glow, soft keyboard typing ambient sound, cinematic 4K, 6 seconds")
    add_scene(story, "SCENE 3 - TOOL #1: ChatGPT / Claude",
        "Number one -- AI writing assistants. You can write scripts, business plans, social media posts in minutes. If you're not using one right now, you're already behind.",
        "Close-up of a glowing chat interface on a dark screen, text appearing letter by letter as if being typed by invisible hands, slow zoom-out to reveal a full futuristic desk setup, neon blue glow, cinematic tech style, subtle typing sound effects and soft UI chime, sharp 4K, 5 seconds")
    add_scene(story, "SCENE 4 - TOOL #2: ElevenLabs",
        "Number two -- ElevenLabs. An AI voice generator so realistic you genuinely cannot tell it from a real human. The secret weapon behind most faceless YouTube channels.",
        "Animated audio waveform pulsing in vibrant neon colors against a dark background, dynamic ripple effect spreading outward from the center, slow rotating camera orbit, futuristic music visualizer style, deep blacks with electric blue and purple glow, rich bass audio pulse sound, cinematic 4K, 5 seconds")
    add_scene(story, "SCENE 5 - TOOL #3: AI Video Generator",
        "Number three -- AI video generators. Type a description and get a cinematic clip in seconds. No camera, no studio, no film crew.",
        "A film clapperboard dissolving into digital particles that reassemble as a stunning cinematic landscape, sweeping wide-angle drone shot over futuristic city skyline at golden hour, seamless morphing transition, cinematic blockbuster style, warm golden and cool blue contrast lighting, epic orchestral swell audio, 4K ultra-sharp, 6 seconds")
    add_scene(story, "SCENE 6 - TOOL #4: Suno AI",
        "Number four -- Suno AI. Original music in any style from just a text prompt. Completely free, completely yours.",
        "Musical notes and sound waves flowing like liquid through a dark digital space, transforming into colorful abstract art patterns, smooth flowing camera pan from left to right, dreamy artistic visualizer style, deep rich colors with glowing neon accents, lush melodic music with gentle beats, cinematic 4K, 5 seconds")
    add_scene(story, "SCENE 7 - TOOL #5: InVideo AI",
        "Number five -- the one that will blow your mind -- InVideo AI. Type your topic and it builds the entire video. Script, voiceover, footage, captions -- everything. This is how thousands of faceless creators are building full-time incomes right now.",
        "A single text prompt on screen exploding into a complete assembled video production -- timelines, footage thumbnails, audio waveforms all appearing simultaneously in a dramatic burst, fast dynamic zoom-in with slight shake, high-energy tech explosion style, bright white and gold light burst, energetic whoosh and impact sound, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 8 - OUTRO / CTA",
        "These 5 tools cost less than $50 a month and can replace an entire creative team. Which one are you starting with? Comment below -- and subscribe for step-by-step tutorials on every single one.",
        "Elegant end screen with five glowing icons arranged in a circle slowly rotating, subscribe button animation pulsing softly in red, dark premium background with subtle particle effects drifting upward, slow gentle zoom-out, luxury tech brand aesthetic, soft blue and white ambient glow, gentle uplifting chime sound, cinematic 4K, 6 seconds")
    story.append(PageBreak())

    # --- VIDEO 2 ---
    add_video_header(story, "This FREE AI Tool Does in 5 Seconds What Takes Designers 5 Hours", "Day 2-3", "TikTok & Reels (60-sec Vertical 9:16)")
    add_scene(story, "SCENE 1 - HOOK",
        "Designers charge $500 for this. This FREE AI tool does it in 5 seconds.",
        "Split screen -- left side a person hunched over a desk working exhausted for hours, right side a glowing AI interface completing the same task instantly with a satisfying ping, vertical 9:16 format, bold contrast lighting, dramatic before-after reveal style, comic impact sound then success chime, sharp 4K vertical, 4 seconds")
    add_scene(story, "SCENE 2 - DEMO",
        "Just type what you need -- a logo, a banner, a full brand kit -- and watch it appear in seconds. No skills needed. No Photoshop. Nothing.",
        "Hands typing a short text prompt on a glowing keyboard, screen instantly fills with beautiful professional design assets appearing one by one, close-up to medium shot camera pull-back, clean minimalist tech style, bright white workspace with soft shadows, satisfying pop and click sound effects, vertical 9:16 4K, 5 seconds")
    add_scene(story, "SCENE 3 - CTA",
        "Follow for more AI tools that are changing everything in 2026.",
        "Bold follow button animation bouncing on screen surrounded by glowing stars and sparkle effects, colorful confetti burst, vertical 9:16 format, fun energetic style, bright vivid colors, upbeat notification sound with pop effect, 4K sharp, 3 seconds")
    story.append(PageBreak())



def build_week2(story):
    # ============================================================
    # WEEK 2
    # ============================================================
    add_week_header(story, "WEEK 2 - BUILD AUDIENCE")

    # --- VIDEO 3 ---
    add_video_header(story, "ChatGPT vs Claude vs Gemini -- Which AI is Actually Best in 2026?", "Day 8", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "Three AI giants. One winner. I tested them all so you don't have to -- and the results shocked me.",
        "Three glowing AI logos facing each other like warriors in an arena, dramatic spotlight on each one, slow rotating 360-degree camera orbit, epic battle cinematic style, dark arena background with electric lightning effects, intense dramatic orchestral sting audio, cinematic 4K, 5 seconds")
    add_scene(story, "SCENE 2 - CHATGPT ROUND",
        "ChatGPT is fast, flexible, and great for everyday tasks. It's the most popular for a reason -- but it has weaknesses.",
        "Glowing ChatGPT interface on a sleek screen with fast text streaming in real-time, dynamic response appearing instantly, medium close-up with slight dolly-in, clean white and green tech aesthetic, bright modern office lighting, fast keyboard typing sound with soft UI chimes, sharp 4K, 5 seconds")
    add_scene(story, "SCENE 3 - CLAUDE ROUND",
        "Claude thinks deeper, writes longer, and reasons more carefully. Perfect for scripts, research and complex tasks.",
        "An elegant dark interface with thoughtful text appearing in well-structured paragraphs, animated brain neural network glowing in the background, slow cinematic pan across the screen, sophisticated dark premium aesthetic, deep purple and white contrast lighting, soft intellectual ambient music, cinematic 4K, 5 seconds")
    add_scene(story, "SCENE 4 - GEMINI ROUND",
        "Gemini connects to Google Search in real time -- giving it something the others don't have. Live, up-to-date information.",
        "Google-colored data streams flowing from the internet globe into an AI interface, real-time web search results populating a screen, sweeping wide shot with zoom-in to screen, vibrant Google color palette on dark background, dynamic energy with streaming light beams, data transmission whoosh sounds, 4K cinematic, 5 seconds")
    add_scene(story, "SCENE 5 - VERDICT + CTA",
        "My verdict? Use ChatGPT for speed, Claude for quality writing, Gemini for research. Use all three and you're unstoppable. Subscribe -- next video I show you exactly how.",
        "Three glowing trophy podiums side by side, each labeled with an AI name, gold silver bronze lighting from above, confetti falling gently, slow majestic zoom-out to wide shot, elegant awards ceremony style, warm gold and white lighting, triumphant fanfare audio, cinematic 4K, 6 seconds")
    story.append(PageBreak())

    # --- VIDEO 4 ---
    add_video_header(story, "Top 3 FREE AI Tools That Replace Expensive Software", "Day 10", "TikTok & Reels (60-sec Vertical 9:16)")
    add_scene(story, "SCENE 1 - HOOK",
        "Stop paying for expensive software. These 3 FREE AI tools do the same thing -- and they're better.",
        "Expensive software logos with red X marks crossed out one by one, replaced by glowing free AI tool icons with green checkmarks, fast-cut vertical 9:16 animation style, bold red and green contrast, sharp impact sounds followed by success chimes, energetic 4K vertical, 4 seconds")
    add_scene(story, "SCENE 2 - TOOLS REVEAL",
        "Number one replaces Photoshop. Number two replaces Premiere Pro. Number three replaces an entire marketing team. All free. All AI. All 2026.",
        "Three glowing AI tool cards flipping into view one by one like playing cards, each revealing a tool name with sparkle effect, dynamic card-flip camera angle, dark premium background with gold accent lighting, satisfying card flip and reveal sound effects, vertical 9:16 4K, 5 seconds")
    add_scene(story, "SCENE 3 - CTA",
        "Follow for the full breakdown of each tool this week.",
        "Notification bell ringing with glowing pulse rings expanding outward, bold FOLLOW text appearing with bounce animation, vertical 9:16 bright colorful style, white background with vibrant accent colors, notification bell ding sound, sharp 4K, 3 seconds")
    story.append(PageBreak())

    # --- VIDEO 5 ---
    add_video_header(story, "The AI Tool Nobody Is Talking About (But Everyone Should Use)", "Day 12", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "This AI tool has been quietly changing how people work -- and almost nobody is talking about it yet. Until now.",
        "A shadowy mysterious door slowly creaking open to reveal blinding white light with a glowing AI interface inside, suspenseful slow push-in camera move, dark thriller cinematic style, dramatic chiaroscuro lighting with deep shadows and bright highlights, tense suspenseful orchestral sound with heartbeat pulse, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 2 - TOOL REVEAL",
        "NotebookLM by Google. You upload any document, any research, any article -- and it instantly becomes a podcast, a summary, a Q&A chatbot. It's like having a personal research team available 24/7 for free.",
        "A stack of documents and research papers being absorbed into a glowing AI brain, transforming into organized knowledge cards and audio waveforms, smooth morphing transition animation, clean academic tech style, soft white and blue lighting with warm gold accents, paper rustling then transformation whoosh sound, cinematic 4K, 6 seconds")
    add_scene(story, "SCENE 3 - USE CASE DEMO",
        "Imagine uploading your competitor's 50-page report and asking it questions. Or turning a boring PDF into a full podcast episode. This is the tool I wish I had years ago.",
        "Split screen showing a dense boring document on the left instantly transforming into an engaging animated podcast waveform on the right, dynamic split-screen reveal with energetic transition, bold contrast style, bright vibrant colors on right vs dull grey on left, before-after transformation sound design, sharp 4K, 5 seconds")
    add_scene(story, "SCENE 4 - CTA",
        "Free. Available right now. Link in the description. And subscribe -- because I have 4 more hidden tools like this dropping this week.",
        "Elegant lower-third text animation with FREE TOOL -- LINK BELOW appearing with smooth slide-in, subscribe button glowing softly in corner, dark background with subtle blue particles floating, slow gentle zoom-in, luxury brand aesthetic, soft chime notification sound, 4K, 4 seconds")
    story.append(PageBreak())



def build_week3(story):
    # ============================================================
    # WEEK 3
    # ============================================================
    add_week_header(story, "WEEK 3 - MONETIZATION FOCUS")

    # --- VIDEO 6 ---
    add_video_header(story, "How to Make $100/Day Using Just AI Tools -- Step by Step", "Day 15", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "$100 a day. Using only AI tools. No experience needed. Here's the exact step-by-step system.",
        "Crisp $100 bills raining down slowly in slow motion against a dark background, glowing AI interface appearing behind the falling cash, dramatic push-in camera move, cinematic luxury money aesthetic, deep black background with gold and green light accents, satisfying cash rustling sound with dramatic bass drop, 4K cinematic, 5 seconds")
    add_scene(story, "SCENE 2 - THE METHOD",
        "Step one -- pick a skill AI can automate. Writing, design, video editing. Step two -- use AI tools to deliver that skill as a service. Step three -- charge clients $50 to $500 per project. Repeat.",
        "A clean numbered roadmap appearing on screen step by step with glowing checkmarks, smooth slide-in animations for each step, professional business infographic style, clean white background with blue and gold accent colors, satisfying checkbox tick sounds for each step, sharp 4K, 6 seconds")
    add_scene(story, "SCENE 3 - SOCIAL PROOF",
        "Thousands of people are already doing this right now -- from their phones, from their bedrooms, from anywhere in the world. The only difference between them and you is they started.",
        "World map with glowing dots appearing across every continent representing creators earning online, camera slowly pulling back to show the full globe, inspiring global scale style, dark background with warm golden glow dots, uplifting orchestral music building to a crescendo, cinematic 4K, 6 seconds")
    add_scene(story, "SCENE 4 - CTA",
        "I'll show you the exact AI tools and clients to target in the next video. Subscribe so you don't miss it.",
        "Bold dynamic text NEXT VIDEO -- THE EXACT TOOLS appearing with energetic bounce animation, subscribe button glowing red with pulse rings, dark background with electric energy particles, fast zoom-in with slight camera shake, hype energy style, notification sound with bass hit, 4K, 5 seconds")
    story.append(PageBreak())

    # --- VIDEO 7 ---
    add_video_header(story, "AI Tools Every Freelancer Needs in 2026", "Day 17", "TikTok & Reels (60-sec Vertical 9:16)")
    add_scene(story, "SCENE 1 - HOOK",
        "If you're a freelancer and not using these AI tools -- you're leaving money on the table every single day.",
        "Money coins and bills floating away from an empty wallet in slow motion, dramatic vertical 9:16 format, emotional cinematic style, desaturated blue tones, sad slow piano note then sudden cut to bright energetic colors as AI tools appear, 4K vertical, 4 seconds")
    add_scene(story, "SCENE 2 - TOOLS LIST",
        "Claude for writing. Canva AI for design. ElevenLabs for voiceovers. Descript for editing. These four alone can 10x your output and let you charge double your rates.",
        "Four glowing tool cards appearing in rapid succession with bold labels, each card snapping into a 2x2 grid formation, fast dynamic vertical 9:16 animation, bold vibrant colors on dark background, rapid snap sound effects with final satisfying click when grid completes, 4K sharp, 5 seconds")
    add_scene(story, "SCENE 3 - CTA",
        "Follow for the full freelancer AI toolkit this week -- completely free.",
        "Freelancer toolkit chest opening to reveal glowing AI tools inside, treasure reveal style vertical 9:16, warm gold and white light spilling out, magical sparkle effects, treasure chest opening sound with magical chime, 4K vertical, 3 seconds")
    story.append(PageBreak())

    # --- VIDEO 8 ---
    add_video_header(story, "I Built a Full Business Using Only AI Tools -- Here's How", "Day 19", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "I built a full business using only AI tools. No employees. No office. No experience. Here's exactly how -- start to finish.",
        "A tiny seed planted in digital soil growing rapidly into a full glowing business empire -- offices, website, money flows all emerging from one small AI spark, time-lapse growth animation, inspiring epic style, dark rich soil transforming to bright golden success, triumphant orchestral build-up, cinematic 4K, 7 seconds")
    add_scene(story, "SCENE 2 - THE STORY",
        "Claude for all my content. Canva AI for designs. ElevenLabs for voiceovers. InVideo to put it all together. The whole stack costs $60 a month.",
        "Clean animated flowchart of connected AI tools forming a business pipeline, each connection lighting up in sequence with a satisfying glow, smooth top-down camera view slowly zooming out, professional infographic motion style, clean white and blue on dark background, sequential connection click sounds, cinematic 4K, 6 seconds")
    add_scene(story, "SCENE 3 - THE RESULTS",
        "The result? A content business that runs almost on autopilot. And the best part -- this same system works for anyone watching this right now.",
        "Revenue graph line shooting dramatically upward in smooth animation, numbers ticking up rapidly on the Y-axis, camera slow push-in on the peak, clean modern data visualization style, green success colors on dark background, rising electronic music with ticker sound and success ding at peak, 4K cinematic, 5 seconds")
    story.append(PageBreak())



def build_week4(story):
    # ============================================================
    # WEEK 4
    # ============================================================
    add_week_header(story, "WEEK 4 - SCALE & REPEAT")

    # --- VIDEO 9 ---
    add_video_header(story, "AI Tools for Students That Will Change How You Study Forever", "Day 22", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "These AI tools would have saved me hundreds of hours in school. If you're a student and not using these -- you're studying the hard way for no reason.",
        "A student surrounded by huge towering stacks of textbooks looking overwhelmed, then AI tools appear and the books compress into a single glowing tablet, dramatic transformation reveal, empathy to relief emotional arc style, dim stressed lighting transforming to bright hopeful glow, relieved sigh to uplifting music transition, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 2 - TOOLS FOR STUDENTS",
        "NotebookLM turns any textbook into a podcast. Claude writes and explains essays. Consensus AI finds real research papers instantly. Otter AI transcribes every lecture automatically.",
        "School desk transforming into a sleek AI-powered study station, each tool appearing as a glowing hologram above the desk in sequence, medium wide shot with slow pan across, futuristic classroom aesthetic, warm study lamp light mixed with cool blue AI glow, soft academic ambient music, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 3 - CTA",
        "Share this with a student who needs to see it. And subscribe -- I have the full guide to each tool coming next week.",
        "Share and subscribe buttons glowing in a clean animated interface, friend notification icon appearing with warm happy pulse effect, clean bright academic style, white background with blue and yellow accents, friendly notification chime sounds, 4K, 4 seconds")
    story.append(PageBreak())

    # --- VIDEO 10 ---
    add_video_header(story, "This AI Voice Generator Sounds More Human Than Real Humans", "Day 24", "TikTok & Reels (60-sec Vertical 9:16)")
    add_scene(story, "SCENE 1 - HOOK",
        "Can you tell which voice is AI and which is human? Most people get it wrong.",
        "Two identical microphones side by side, one labeled HUMAN one labeled AI, question marks floating above both, dramatic spotlight effect, vertical 9:16 format, dark mysterious style, tension-building drum roll sound, sharp 4K vertical, 4 seconds")
    add_scene(story, "SCENE 2 - THE REVEAL",
        "ElevenLabs just released voices so realistic that voice actors are genuinely paying attention. 30 languages. Any accent. Any emotion. And you can clone your own voice in minutes.",
        "Animated voice waveform transforming into multiple different waveforms representing different languages and accents, globe spinning with audio waves emanating from it, dynamic vertical 9:16 visualization, vibrant neon colors on deep black, multilingual ambient sound design, 4K sharp, 5 seconds")
    add_scene(story, "SCENE 3 - CTA",
        "Follow -- I'll show you exactly how to set it up for free in my next video.",
        "Microphone transforming into a follow button with satisfying morph animation, vertical 9:16 bold style, bright white and electric blue, energetic swoosh transformation sound with notification chime, 4K vertical, 3 seconds")
    story.append(PageBreak())

    # --- VIDEO 11 ---
    add_video_header(story, "How to Create a Faceless YouTube Channel Using Only AI Tools", "Day 26", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - HOOK",
        "You don't need a camera. You don't need your face. You don't even need to record your own voice. Here's how to build a full YouTube channel using only AI tools.",
        "A YouTube play button materializing from pure digital code and particles, no human face anywhere in frame, just AI energy and data assembling into a complete channel, dramatic build-up reveal style, dark digital space with red YouTube accent colors, building electronic music culminating in a bold impact, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 2 - THE FULL WORKFLOW",
        "Script with Claude. Voice with ElevenLabs. Video with Seedance 2. Captions with CapCut. Thumbnail with Canva AI. Schedule with Buffer. That's it. That's the entire system.",
        "Clean animated workflow pipeline with 6 connected glowing nodes each lighting up in sequence -- script, voice, video, captions, thumbnail, schedule -- forming a complete circle, smooth professional motion graphic style, white nodes on dark blue background with connecting light beams, sequential activation sounds with satisfying final completion chime, 4K cinematic, 7 seconds")
    add_scene(story, "SCENE 3 - MOTIVATION + CTA",
        "The channel you're watching right now was built with this exact system. If I can do it -- so can you. Subscribe and I'll walk you through every single step.",
        "Motivational journey shot -- a single path of light stretching forward into a bright horizon, subscribe button appearing at the end of the path glowing warmly, slow cinematic dolly-forward shot, inspiring hopeful style, warm golden light at horizon against deep blue sky, uplifting orchestral music swelling to close, 4K cinematic, 6 seconds")
    story.append(PageBreak())

    # --- VIDEO 12 ---
    add_video_header(story, "Month 1 Complete -- What I Learned + What's Coming Next", "Day 30", "YouTube (Long-form)")
    add_scene(story, "SCENE 1 - RECAP",
        "Month one is done. Here's everything I learned about building a faceless AI tools channel -- the wins, the mistakes, and what I'm doing differently in month two.",
        "Calendar pages flipping rapidly showing 30 days passing, then stopping on Day 30 with a gold star stamp, cinematic time passage style, warm nostalgic feeling, soft golden tones with paper texture, calendar page flipping sounds ending with a satisfying gold stamp impact, 4K cinematic, 5 seconds")
    add_scene(story, "SCENE 2 - LESSONS LEARNED",
        "Consistency beats perfection. Short-form drives traffic to long-form. AI tools save 80% of production time. The audience that shows up in month one stays forever if you serve them well.",
        "Four wisdom quote cards appearing one by one with elegant fade-in animations, each with a simple icon and bold text, thoughtful premium editorial style, dark background with warm cream card colors and gold accents, soft page turn sound for each card, 4K cinematic, 6 seconds")
    add_scene(story, "SCENE 3 - MONTH 2 TEASE + CTA",
        "Month two starts now -- and it's going to be bigger. Subscribe and turn on notifications so you don't miss a single video.",
        "Dramatic rocket launching upward from a dark launchpad into a star-filled sky, leaving a golden trail behind, camera tracking upward with the rocket, epic cinematic launch style, deep dark background with fire glow and star shimmer, thunderous rocket launch sound building to a triumphant orchestral close, 4K cinematic, 7 seconds")
    story.append(PageBreak())



def build_quick_reference(story):
    # ============================================================
    # FINAL PAGE -- QUICK REFERENCE
    # ============================================================
    add_week_header(story, "QUICK REFERENCE -- SEEDANCE 2 PROMPT FORMULA")

    story.append(Paragraph("The Golden Formula", scene_style))
    story.append(Paragraph(
        "[SUBJECT] + [ACTION] + [CAMERA MOVE] + [STYLE] + [LIGHTING] + [AUDIO] + [DURATION]",
        prompt_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Camera Moves Cheat Sheet", scene_style))
    camera_moves = [
        "Push-in / Dolly-in -- builds tension, draws viewer in",
        "Zoom-out / Pull-back -- reveals scale, epic feeling",
        "360 Orbit -- dramatic, showcases subject from all angles",
        "Pan Left / Pan Right -- smooth reveal, storytelling",
        "Tracking Shot -- follows action, dynamic energy",
        "Top-down / Birds Eye -- infographic, map, overview content",
    ]
    for cm in camera_moves:
        story.append(Paragraph(f"- {cm}", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Style Keywords That Work Best in Seedance 2", scene_style))
    styles_list = [
        "Cinematic 4K / 8K -- premium, professional look",
        "Sci-fi futuristic -- great for AI & tech content",
        "Dark premium aesthetic -- luxury, high-end feel",
        "Clean minimalist -- modern, corporate, trustworthy",
        "Vertical 9:16 -- always specify for TikTok & Reels",
        "Warm golden tones -- emotional, inspiring, nostalgic",
        "Deep contrast / Chiaroscuro -- dramatic, suspenseful",
    ]
    for s in styles_list:
        story.append(Paragraph(f"- {s}", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Full Workflow Stack", scene_style))
    workflow = [
        "1. SCRIPT     -> Claude / ChatGPT",
        "2. VOICEOVER  -> ElevenLabs",
        "3. VIDEO      -> Seedance 2",
        "4. CAPTIONS   -> CapCut",
        "5. THUMBNAIL  -> Canva AI",
        "6. MUSIC      -> Suno AI",
        "7. SCHEDULE   -> Buffer / Later",
    ]
    for w in workflow:
        story.append(Paragraph(w, prompt_style))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Created with Kiro AI & Claude AI (Anthropic) -- AI Tools Faceless Channel -- 2026", note_style))
    story.append(Paragraph("Optimized for Seedance 2 by ByteDance", note_style))


def main():
    """Main entry point -- builds the PDF with full error handling."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    try:
        story = build_story()
        build_week1(story)
        build_week2(story)
        build_week3(story)
        build_week4(story)
        build_quick_reference(story)
        doc.build(story)
        print(f"PDF successfully created: {OUTPUT_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to build PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
