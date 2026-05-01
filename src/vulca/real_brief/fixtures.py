"""Built-in public creative brief fixtures for the real-brief benchmark."""
from __future__ import annotations

from vulca.real_brief.types import (
    REVIEW_DIMENSIONS,
    Deliverable,
    RealBriefFixture,
    SourceInfo,
    safe_slug,
)


def _dims() -> list[str]:
    return list(REVIEW_DIMENSIONS)


def build_real_brief_fixtures() -> list[RealBriefFixture]:
    return [
        RealBriefFixture(
            slug="gsm-community-market-campaign",
            title="Glenwood Sunday Market Campaign System",
            source=SourceInfo(
                url=(
                    "https://rpba.org/wp-content/uploads/2026/02/"
                    "Marketing-Creative-Services-for-GSM-RFP-2026.pdf"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Rogers Park Business Alliance / Glenwood Sunday Market",
            context=(
                "Community farmers market marketing system for a 19-week 2026 "
                "market season."
            ),
            audience=[
                "local shoppers",
                "SNAP and matching-program participants",
                "vendors and community partners",
            ],
            deliverables=[
                Deliverable("content framework", "19-week system", "planning"),
                Deliverable("social templates", "editable Canva templates", "social"),
                Deliverable("banner concepts", "market signage", "print"),
                Deliverable("sticker and tote concepts", "merchandise preview", "print"),
            ],
            constraints=[
                "must use existing logo, colors, and fonts",
                "must use real photography",
                "must avoid illustrations and clip art",
                "must remain Canva-editable",
            ],
            budget="$5,000",
            timeline="2026 market season",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "generic farmers market aesthetic",
                "template set not reusable for 19 weeks",
                "visual system not editable by the client",
            ],
            avoid=["clip art", "illustration-first campaign", "single poster only"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Design a reusable community market campaign system with evergreen "
                "templates, real-photo usage rules, social examples, and print/merch "
                "preview assets."
            ),
            domain="brand_visual",
            tags=["campaign", "community", "templates"],
        ),
        RealBriefFixture(
            slug="seattle-polish-film-festival-poster",
            title="Seattle Polish Film Festival Poster",
            source=SourceInfo(
                url="https://www.polishfilms.org/submit-a-poster",
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Seattle Polish Film Festival",
            context="Signature poster concept for the 34th festival edition.",
            audience=[
                "festival attendees",
                "Polish cinema community",
                "Seattle arts audience",
            ],
            deliverables=[
                Deliverable("poster concept", "11 x 17 in vertical", "print/digital"),
                Deliverable("program cover adaptation", "same key art", "print"),
            ],
            constraints=[
                "required festival text must be present",
                "dates, venues, website, and producer line must be accounted for",
                "bottom sponsor or patron logo band must remain available",
                "print output should anticipate CMYK and 300 dpi production",
            ],
            budget="not specified by source",
            timeline="source-specific contest deadline",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "broken generated text",
                "unsafe margins",
                "generic Polish national symbolism",
                "missing sponsor band",
            ],
            avoid=["illegible typography", "crowded logo area", "flag-only concept"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Create layout-safe poster concept directions for a Polish film "
                "festival, including required text strategy, margins, sponsor band, "
                "and print-risk notes."
            ),
            domain="poster",
            tags=["poster", "film", "layout"],
        ),
        RealBriefFixture(
            slug="model-young-package-unpacking-taboo",
            title="Model Young Package 2026: Unpacking Taboo",
            source=SourceInfo(
                url=(
                    "https://www.modelgroup.com/language-masters/en/"
                    "model-young-package.html"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Model Young Package",
            context=(
                "Paper or cardboard packaging concept around sensitive or "
                "stigmatized topics."
            ),
            audience=["competition jury", "design educators", "social-impact brands"],
            deliverables=[
                Deliverable("packaging concept", "paper/cardboard structure", "product"),
                Deliverable("unboxing flow", "step sequence", "prototype planning"),
                Deliverable("structure diagram prompt", "blueprint-style view", "planning"),
            ],
            constraints=[
                "must be respectful toward taboo-adjacent subject matter",
                "must consider manufacturability",
                "must consider sustainability and material economy",
                "must explain function and ergonomics",
            ],
            budget="competition entry; production budget not specified",
            timeline="2026 competition cycle",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "sensationalizing sensitive topics",
                "beautiful render without structural logic",
                "unmanufacturable packaging form",
            ],
            avoid=["shock-value visuals", "decorative box only", "plastic-first concept"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Design a paper-based packaging proposal for a taboo-adjacent "
                "product with respectful concept, structure, unboxing sequence, "
                "material constraints, and prototype-oriented visuals."
            ),
            domain="packaging",
            tags=["packaging", "structure", "social-design"],
        ),
        RealBriefFixture(
            slug="erie-botanical-gardens-public-art",
            title="Buffalo and Erie County Botanical Gardens Public Art",
            source=SourceInfo(
                url=(
                    "https://www4.erie.gov/publicart/"
                    "2026-call-artists-buffalo-and-erie-county-botanical-gardens"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Erie County / Buffalo and Erie County Botanical Gardens",
            context=(
                "Site-specific public art proposal for a botanical garden setting."
            ),
            audience=["public art panel", "garden visitors", "local community"],
            deliverables=[
                Deliverable("artist proposal", "concept package", "proposal"),
                Deliverable("site-response rationale", "written narrative", "proposal"),
                Deliverable("installation sketch prompts", "visual thumbnails", "planning"),
            ],
            constraints=[
                "must respond to site history and future",
                "must address durability and maintenance",
                "must include installation and engineering assumptions",
                "must respect public access and safety",
            ],
            budget="up to $75,000",
            timeline="2026 public art process",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "gallery object rather than site-specific public work",
                "missing maintenance plan",
                "budget fantasy",
            ],
            avoid=["temporary-looking materials", "unanchored decorative sculpture"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Create a site-specific public art proposal package with concept, "
                "site rationale, material palette, installation assumptions, "
                "maintenance risks, budget notes, and review thumbnails."
            ),
            domain="public_art",
            tags=["public-art", "site-specific", "proposal"],
        ),
        RealBriefFixture(
            slug="music-video-treatment-low-budget",
            title="Low-Budget Music Video Treatment",
            source=SourceInfo(
                url="https://creative-commission.com/briefs/brief-10642",
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Music artist / label brief",
            context=(
                "Director or producer treatment for a low-budget music video, "
                "with AI elements allowed by the brief."
            ),
            audience=["artist team", "label commissioner", "director shortlist panel"],
            deliverables=[
                Deliverable("director treatment", "written concept", "pitch"),
                Deliverable("mood frames", "visual references", "pitch"),
                Deliverable("scene beats", "sequence outline", "production planning"),
            ],
            constraints=[
                "must fit low-budget execution",
                "must disclose AI-use approach",
                "must not assume expensive locations or large crew",
                "must avoid asking for unpaid full treatment before shortlist",
            ],
            budget="about GBP 1,000",
            timeline="source-specific commission window",
            required_outputs=["decision_package", "production_package"],
            ai_policy="allowed",
            simulation_only=True,
            risks=[
                "overproduced concept",
                "moodboard without executable scenes",
                "unclear AI disclosure",
            ],
            avoid=["large crew assumptions", "expensive VFX-heavy production"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Simulate a shortlisted director treatment with concept, mood "
                "frames, scene structure, production constraints, AI-use disclosure, "
                "and deliverables plan."
            ),
            domain="video_treatment",
            tags=["video", "treatment", "low-budget"],
        ),
    ]


def get_real_brief_fixture(slug: str) -> RealBriefFixture:
    safe = safe_slug(slug)
    for fixture in build_real_brief_fixtures():
        if fixture.slug == safe:
            return fixture
    known = ", ".join(fixture.slug for fixture in build_real_brief_fixtures())
    raise ValueError(f"unknown real brief slug: {slug!r}; expected one of: {known}")
