import json
import base64
import streamlit as st
from pathlib import Path

try:
    import fitz
    HAVE_PYMUPDF = True
except Exception:
    HAVE_PYMUPDF = False

st.set_page_config(
    page_title="Portfolio Showcase: Projects I'm Proud Of",
    page_icon="📁",
    layout="wide",
)

ASSETS = Path("assets")
RESUME_PATH = ASSETS / "Ta-asan Ralph Vincent - Résumé.pdf"
SIGNATURE_PATH = ASSETS / "signature1.png"

@st.cache_data
def load_projects():
    pj = Path("projects.json")
    if not pj.exists():
        st.error(
            "Missing `projects.json`. Create it in the same folder as this file. "
            "Also add your PNGs under `assets/`."
        )
        return []
    data = json.loads(pj.read_text(encoding="utf-8"))
    return sorted(data, key=lambda d: d["title"].lower())

@st.cache_data(ttl=60)
def load_experiences_with_ttl():
    xp = Path("experiences.json")
    if not xp.exists():
        return []
    return json.loads(xp.read_text(encoding="utf-8"))

experiences = load_experiences_with_ttl()

projects = load_projects()
experiences = load_experiences()

st.sidebar.title("Explore Projects")

st.session_state["wide"] = st.sidebar.toggle(
    "Two-column layout",
    value=True,
    help="Turn off for a single-column (mobile) list."
)

all_tags = sorted({t for p in projects for t in p.get("tags", [])})
query = st.sidebar.text_input("Search title")
selected = st.sidebar.multiselect("Filter by tags", options=all_tags)

def render_card(p):
    col_img, col_txt = st.columns([1, 2], gap="medium")

    with col_img:
        img_path = ASSETS / p["image"]
        if img_path.exists():
            st.image(str(img_path), use_container_width=True, clamp=True)
        else:
            st.markdown(f"🖼️ *Missing image:* `{p['image']}`")
            st.caption("Place it under `assets/` with this exact filename.")

    with col_txt:
        st.subheader(p["title"])
        if p.get("tags"):
            st.caption(", ".join(p["tags"]))
        st.write(p.get("blurb", ""))

        links = p.get("links", {})
        if links:
            n = min(4, len(links))
            link_cols = st.columns(n, gap="small")
            for (label, url), c in zip(links.items(), link_cols):
                with c:
                    st.link_button(label, url)

def matches(p):

    if selected and not set(selected).intersection(set(p.get("tags", []))):
        return False

    if query:
        q = query.lower()
        text = (p["title"] + " " + p.get("blurb", "")).lower()
        if q not in text:
            return False
    return True

def render_showcase():
    filtered = [p for p in projects if matches(p)]

    st.title("Portfolio Showcase: Projects I'm Proud Of")
    st.markdown(
        "Hi, I'm Ralph Vincent Ta-asan — a data storyteller, strategist, and an explorer. "
        "Here’s a curated selection of the projects I’ve poured my heart and skills into, spanning data science, business intelligence, creative tech, and strategic research. "
        "Use the filters on the left to explore how I think, build, and tell stories through data."
    )
    st.write(f"Showing **{len(filtered)}** of **{len(projects)}** projects.")

    if st.session_state.get("wide", True):
        cols = st.columns(2, gap="large")
        for i, p in enumerate(filtered):
            with cols[i % 2]:
                render_card(p)
                st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    else:
        for p in filtered:
            render_card(p)
            st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

def render_resume():
    st.title("Electronic Résumé")
    st.caption("View inline, print directly, or download the PDF version.")

    if not RESUME_PATH.exists():
        st.error(f"Résumé file not found at: {RESUME_PATH}")
        st.info("Place your PDF in the assets/ folder with that exact filename.")
        return

    pdf_bytes = RESUME_PATH.read_bytes()
    st.download_button(
        label="Download Résumé (PDF)",
        data=pdf_bytes,
        file_name=RESUME_PATH.name,
        mime="application/pdf",
        use_container_width=True,
    )

    mode = st.radio(
        "Viewer",
        options=["Clean", "Standard"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "Clean":
        if not HAVE_PYMUPDF:
            st.info("For the clean viewer, install PyMuPDF: `pip install pymupdf`")
        else:

            display_px = st.slider(
                "Résumé width",
                min_value=600, max_value=1200, value=900, step=50,
                help="Adjust how wide the rendered pages appear."
            )

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                left, mid, right = st.columns([1, 4, 1])
                with mid:
                    st.image(pix.tobytes("png"), width=display_px)
            return

    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f"""
        <iframe
            src="data:application/pdf;base64,{b64}#toolbar=0&navpanes=0&scrollbar=0&zoom=page-width"
            style="width:100%; height:1000px; border:none; border-radius:12px;"
        ></iframe>
        """,
        unsafe_allow_html=True,
    )

def render_experiential():
    st.title("Experiential Learning")
    st.caption("Volunteer work, student organization involvement, apprenticeships, field trips, special projects and employment. Upload and describe photos, job descriptions and completed projects.")

    if not experiences:
        st.info("Add items to `experiences.json` and images to `assets/` to populate this page.")
        return

    mode = st.radio("Layout", ["Feature", "Cards"], horizontal=True, label_visibility="collapsed")

    if mode == "Feature":
        for exp in experiences:

            img_path = ASSETS / exp.get("image", "")
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)

            st.markdown(f"## {exp.get('title','')}")
            meta = " - ".join(filter(None, [exp.get("date", ""), ", ".join(exp.get("tags", []))]))
            if meta:
                st.caption(meta)

            if exp.get("lede"):
                st.markdown(f"<p style='font-size:1.05rem;line-height:1.7'><em>{exp['lede']}</em></p>", unsafe_allow_html=True)

            facts = exp.get("facts", [])
            if facts:
                with st.expander("Quick facts", expanded=True):
                    for f in facts:
                        st.markdown(f"- {f}")

            if exp.get("body_md"):
                st.markdown(exp["body_md"])
            st.divider()
    else:
        cols = st.columns(2, gap="large")
        for i, exp in enumerate(experiences):
            with cols[i % 2]:
                img_path = ASSETS / exp.get("image", "")
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                st.subheader(exp.get("title",""))
                if exp.get("date"): st.caption(exp["date"])
                if exp.get("lede"): st.write(exp["lede"])
                if exp.get("body_md"):
                    with st.expander("Read more"):
                        st.markdown(exp["body_md"])
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

def render_reflections():
    st.title("*I've always loved numbers. But never quite like this.*")

    reflections_md = """
I still remember the exact moment I felt something shift. It wasn’t a grand event, a medal, a recognition, or even a final exam. It was in a quiet lecture hall, the kind where most students tune out after the first hour. I had just run my very first regression. What struck me wasn’t the math; it was how the data spoke. It whispered back a pattern, a direction, a meaning. In that moment I realized that learning wasn’t just about numbers or performance; it was about listening. In many ways that small whisper from the data became the loudest voice in my entire college journey.

I didn’t begin my college years with this clarity. Like many students, I entered school with the mindset of accumulation. I thought the goal was to collect lectures, handouts, readings, and definitions. I over-consumed knowledge as if success were a matter of quantity. It felt like moving into a tiny condo and buying every piece of furniture I saw online. I filled my mental space with everything, hoping that if I just stored enough, I would become the kind of student who “had it all.” Instead I ended up cluttered, confused, and overwhelmed. I was burnt out, and my grades reflected it. It wasn’t until I slowed down that I understood real learning isn’t about remembering everything; it’s about curating what truly matters. That was the beginning of my “capsule life” philosophy. If I had to pack all my learnings into a small capsule to carry into the future, what would I choose to keep? What beliefs, skills, and mindsets are truly worth carrying forward? This shift, from hoarding knowledge to keeping only what’s essential, quietly transformed how I approached life, work, and learning.

The lesson deepened during a morning walk when I realized something else. I want to grow in many aspects of life, yet I cannot grow in all of them simultaneously without compromise. I thought about random dreams: learning to crochet, completing the Google Data Analytics course, building a game in Unreal Engine, writing a book, making music. All are exciting, but to get good at something and see real results, I must commit for a long time. Trying to do everything would leave me a master of none. Just as I can name the shoes I no longer wear and the gadgets I no longer use, I can name the skills and dreams that truly matter to me now. To under-consume, I had to over-consume first. I had to try things to make sure they weren’t for me. From that I learned the same is true for knowledge: to surround myself with what matters, I must choose with intention.

Another pivotal turning point came when I realized I had been working for grades, not for growth. It’s easy to fall into that trap where everything centers on output: final scores, rubrics, checklists. Yet grades are the wrong kind of fuel; they burn fast and leave you empty. Only when I started doing projects for joy, curiosity, and the simple excitement of solving something meaningful did things begin to change. I remember stumbling upon a Taylor Swift lyric, “to live for the hope of it all”. That line stuck not as romance but as a question: what does it mean to hope? Can hope be measured? Could there be a formula for staying, trying, and believing in the possibility of something good?

It might seem unusual to begin a reflection on how numbers changed my life with a pop lyric. She wasn’t talking mathematics, yet her words felt like a personal challenge. Will hope ever come? Is there truly hope in it all? Can a formula prove it, a way to measure the chance of something happening at least once?

Statistics has an answer.

Life often feels like a race. You may not be the fastest, the strongest, or anywhere near the front, but what if you simply stayed? What if you kept showing up long after others stopped? You might remain the slowest, yet when you’re the only one left, you find yourself in first place.

Life isn’t a single probability; it’s a collection layered over time. Some events are beyond control, while others tilt in our favor simply by showing up. The probability of something happening at least once after n attempts is 1 − (1 − p)ⁿ, where p is success on one try, 1 − p is failure on one try, and n is the number of attempts.

Try once and your chance is merely p. Try twice and the failure chance multiplies by itself, shrinking to 25 percent if 1 - p equals 50 percent. Three tries reduce it further. Ten tries, a hundred tries; eventually the chance of it not happening becomes so small that life has no choice but to let it happen.

This formula says that if you try enough times, success arrives at least once. Beyond mathematics lies presence. How can you live for the hope of it all if you remove every chance by never showing up? Be the person who stays; be the person who tries again. Turn up for the 0.0001 percent chance, because if not today, perhaps tomorrow. In an uncertain world, statistics remain certain, and when you keep showing up, the math eventually whispers, “Fine. You win.”

Live for the hope of it all, not because certainty awaits, but because you stayed until the odds had no choice but to choose you. Do what you love. Pursue what excites you even when odds stand against you. Keep doing the work even when the only certainty is the chance itself. The more you try, the more hope must find you. So keep showing up; stay in the race; live for the hope of it all, because the formula says it’s worth it.

As my mindset evolved, so did my view of what I studied. Business Intelligence and Analytics was not merely a major; it became a language. Data turned into my lens for seeing the world. From Python scripts to Power BI dashboards, I grew excited not just by answers but by stories hidden in rows and columns. Each column is a decision; each row, a consequence. My mission is to uncover the “why” behind the “what.” Storytelling through data isn’t about flash; it’s about clarity and humanity.

This realization crystallized during my internship at McKupler Inc. I arrived convinced I must dazzle with models and dashboards, yet my impact came from small acts: cleaning messy headers, mapping hubs, writing a reconciliation script, and standardizing product names. They weren’t dramatic, yet they made others’ work easier. I found purpose not in impressing, but in being useful, helping the team move forward. Data work isn’t always glamorous. Often it’s quiet, simply easing someone’s job, and that, to me, is more than enough.

Looking ahead, I view my career not as a mere pursuit of analytics but as a lifelong practice in storytelling that turns raw numbers into living context. I want products that remember why something was saved, who it served, and which emotion accompanied it.

One idea I nurture is Keep, an app storing shared links like messages to a friend while remembering intention. Another is my fascination with Pokémon analytics, using reinforcement learning to simulate battles for insight beyond victory. I aim to master AI automation, crafting workflows that let businesses scale without losing human context, echoing the automation I built for McKupler. That project showed how data paired with AI reshapes work, granting clarity and freeing people for what matters.

My future aligns with ikigai; the intersection of what I love, what I’m good at, what the world needs, and what earns a living. Passion joins what I love and what I excel at: data storytelling, competitive Pokémon strategy, intuitive systems. Vocation joins what the world needs and what pays: businesses crave clear data, governments seek efficient systems, communities deserve meaningful tech. Mission joins what I love and what the world needs: tools like Keep that simplify life rather than overwhelm it. Profession joins skills and income: Python, Power BI, AI workflow design meeting market demand.

At the center sits ikigai, my compass for every decision. And I remind myself: I am blessed to even be here. Blessed and privileged to find discomfort in the very path I chose, because it means I am swimming in the ocean I once longed to reach. How fortunate I am to struggle in the waves I once prayed to stand in. How fortunate I am to be exhausted from chasing the very thing I once only dreamed of touching.

With that perspective, I set five promises. Number one, anything above zero compounds; small actions matter. Number two, I will show up for the 0.0001 percent; consistency bends odds. Number three, I will curate my tools, keeping only what I can master and use. Number four, story first, numbers second; meaning outweighs metrics. Lastly, I will leave things better, whether dataset, process, or person.

If I packed college into a capsule, it wouldn’t hold every lecture or assignment. I’d keep the formula of hope, the passion for storytelling, the joy-filled projects, the skills I intend to master, and lessons for a lifetime. I may not know exactly where I’ll be in five years, yet I will still be trying, still showing up, still living for the hope of it all.

To Benilde, I have a question. It might seem strange to ask just before graduating, but how do I really be like no other? Until now, I have no clue. Is it about being our own person, as we are all made of different numbers of atoms, different numbers of brain cells, and different numbers of seconds lived in this life? Is it about being so radically different even if I’d want to find inspiration in the numbers of someone else? But maybe it’s not about being like no other but being who I want to be, even if it’s like another. Maybe it’s not about being like no other, but embracing our life’s data will never be like Taylor Swift, will never be like Barack Obama, or will never be like Victor Wembanyama. But that’s okay; I can have my own numbers in the encounters I’ve had in life, yet find a pattern to trace similarities in the lives that I want to follow. To draw similarities in the lives that inspired me. In that way, I can be myself; in that way, I can be limitless; in that way, I can stay, and in that way, I can continue loving numbers. I’ve had a million experiences in Benilde. Each and every one of those, I treasure deeply in my heart. I have lived a life loving numbers, but honestly, *I’ve never loved them quite like this*.
"""

    st.markdown(
        "<div style='font-size:1.05rem; line-height:1.85'>"
        + reflections_md.replace("\n\n", "<br><br>")
        + "</div>",
        unsafe_allow_html=True,
    )

    if SIGNATURE_PATH.exists():
        spacer, sigcol = st.columns([5, 2])
        with sigcol:
            st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
            st.image(str(SIGNATURE_PATH), use_container_width=True)
            st.markdown("<em>Ralph Vincent Ta-asan</em>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:

        spacer, sigcol = st.columns([5, 2])
        with sigcol:
            st.markdown("<div style='text-align:right;'><em>Ralph Vincent Ta-asan</em></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📁 Portfolio Showcase",
    "📄 Electronic Résumé",
    "📰 Experiential Learning",
    "🖊️ Reflections"
])

with tab1:
    render_showcase()
with tab2:
    render_resume()
with tab3:
    render_experiential()
with tab4:
    render_reflections()
