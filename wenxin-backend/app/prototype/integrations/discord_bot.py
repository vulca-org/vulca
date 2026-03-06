"""VULCA Discord Bot — CultureAdvisor for real-time community interaction.

Setup:
    1. Create a Discord Application at https://discord.com/developers
    2. Enable "Message Content Intent" in Bot settings
    3. Set env vars: DISCORD_BOT_TOKEN, VULCA_API_URL, VULCA_API_KEY
    4. Invite bot with scopes: bot, applications.commands
       Permissions: Send Messages, Embed Links, Attach Files, Use Slash Commands

Run:
    python -m app.prototype.integrations.discord_bot

Commands:
    /vulca evaluate [image] [tradition]  — L1-L5 cultural evaluation
    /vulca identify [image]              — Identify cultural tradition
    /vulca tradition [name]              — Look up tradition details
    /vulca ask [question]                — Cultural knowledge Q&A (Gemini)
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
VULCA_API_URL = os.environ.get("VULCA_API_URL", "http://localhost:8001")
VULCA_API_KEY = os.environ.get("VULCA_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

TRADITION_CHOICES = [
    ("Auto-detect", "auto"),
    ("Chinese Xieyi", "chinese_xieyi"),
    ("Chinese Gongbi", "chinese_gongbi"),
    ("Western Academic", "western_academic"),
    ("Islamic Geometric", "islamic_geometric"),
    ("Japanese Traditional", "japanese_traditional"),
    ("Watercolor", "watercolor"),
    ("African Traditional", "african_traditional"),
    ("South Asian", "south_asian"),
]

# Score bar helper
def _score_bar(score: float, width: int = 10) -> str:
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)


async def _api_post(endpoint: str, body: dict) -> dict:
    """Async POST to VULCA API."""
    import httpx

    headers = {"Content-Type": "application/json"}
    if VULCA_API_KEY:
        headers["Authorization"] = f"Bearer {VULCA_API_KEY}"

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            f"{VULCA_API_URL}{endpoint}",
            json=body,
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


async def _gemini_ask(question: str) -> str:
    """Ask Gemini a cultural art question."""
    if not GEMINI_API_KEY:
        return "Gemini API key not configured. Set GEMINI_API_KEY env var."

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = (
            "You are VULCA CultureAdvisor, an expert on cultural art traditions. "
            "You specialize in 9 traditions: Chinese Xieyi, Chinese Gongbi, Western Academic, "
            "Islamic Geometric, Japanese Traditional, Watercolor, African Traditional, South Asian, "
            "and cross-cultural art theory. "
            "The VULCA L1-L5 framework evaluates: L1 Visual Perception, L2 Technical Analysis, "
            "L3 Cultural Context, L4 Critical Interpretation, L5 Philosophical Aesthetic. "
            "Answer concisely (under 300 words), relating to specific traditions and L-levels when relevant.\n\n"
            f"Question: {question}"
        )

        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text[:1900]  # Discord embed limit
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return f"Error consulting Gemini: {e}"


def build_bot():
    """Build and return the Discord bot. Requires discord.py."""
    try:
        import discord
        from discord import app_commands
    except ImportError:
        raise ImportError("Install discord.py: pip install discord.py")

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    # --- /vulca evaluate ---
    @tree.command(name="vulca-evaluate", description="Evaluate an image for cultural quality (L1-L5)")
    @app_commands.describe(
        image="Image to evaluate",
        tradition="Cultural tradition (default: auto-detect)",
    )
    @app_commands.choices(tradition=[
        app_commands.Choice(name=label, value=val)
        for label, val in TRADITION_CHOICES
    ])
    async def cmd_evaluate(
        interaction: discord.Interaction,
        image: discord.Attachment,
        tradition: Optional[str] = "auto",
    ):
        await interaction.response.defer(thinking=True)

        try:
            img_bytes = await image.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            body: dict = {"image_base64": img_b64}
            if tradition and tradition != "auto":
                body["tradition"] = tradition

            result = await _api_post("/api/v1/evaluate", body)

            scores = result.get("scores", {})
            total = result.get("weighted_total", 0)
            trad = result.get("tradition_used", "unknown")
            diagnosis = result.get("cultural_diagnosis", "")
            risks = result.get("risk_flags", [])
            latency = result.get("latency_ms", 0)

            embed = discord.Embed(
                title="VULCA Cultural Evaluation",
                color=0x007AFF,
            )
            embed.set_thumbnail(url=image.url)

            # Scores field
            score_lines = []
            dim_names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophic"}
            for key, label in dim_names.items():
                s = scores.get(key, 0)
                score_lines.append(f"{label}: {s:.2f} {_score_bar(s)}")
            embed.add_field(name="L1-L5 Scores", value="\n".join(score_lines), inline=False)

            embed.add_field(name="Total", value=f"**{total:.3f}**", inline=True)
            embed.add_field(name="Tradition", value=trad, inline=True)
            embed.add_field(name="Latency", value=f"{latency}ms", inline=True)

            if diagnosis:
                embed.add_field(name="Diagnosis", value=diagnosis[:1024], inline=False)

            if risks:
                embed.add_field(name="Risk Flags", value="\n".join(f"⚠️ {r}" for r in risks[:3]), inline=False)

            embed.set_footer(text="vulcaart.art | VULCA Cultural AI Framework")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error("Evaluate error: %s", e)
            await interaction.followup.send(f"Error: {e}")

    # --- /vulca identify ---
    @tree.command(name="vulca-identify", description="Identify the cultural tradition of an image")
    @app_commands.describe(image="Image to analyze")
    async def cmd_identify(interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(thinking=True)

        try:
            img_bytes = await image.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            result = await _api_post("/api/v1/identify-tradition", {"image_base64": img_b64})

            tradition = result.get("tradition", "unknown")
            confidence = result.get("confidence", 0)
            alternatives = result.get("alternatives", [])

            embed = discord.Embed(
                title="Tradition Identification",
                description=f"**{tradition}** (confidence: {confidence:.0%})",
                color=0x34C759,
            )
            embed.set_thumbnail(url=image.url)

            if alternatives:
                alt_text = "\n".join(f"- {a.get('tradition', '?')}: {a.get('confidence', 0):.0%}" for a in alternatives[:5])
                embed.add_field(name="Alternatives", value=alt_text, inline=False)

            weights = result.get("recommended_weights", {})
            if weights:
                w_text = " | ".join(f"{k}: {v:.2f}" for k, v in sorted(weights.items()))
                embed.add_field(name="Recommended Weights", value=w_text, inline=False)

            embed.set_footer(text="vulcaart.art")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    # --- /vulca tradition ---
    @tree.command(name="vulca-tradition", description="Look up a cultural tradition's details")
    @app_commands.describe(name="Tradition name")
    @app_commands.choices(name=[
        app_commands.Choice(name=label, value=val)
        for label, val in TRADITION_CHOICES if val != "auto"
    ])
    async def cmd_tradition(interaction: discord.Interaction, name: str):
        try:
            from app.prototype.cultural_pipelines.tradition_loader import get_tradition
            tc = get_tradition(name)
        except ImportError:
            tc = None

        if not tc:
            await interaction.response.send_message(f"Tradition `{name}` not found.")
            return

        embed = discord.Embed(
            title=tc.display_name.get("en", tc.name),
            color=0xFF9500,
        )

        # Weights
        w_text = " | ".join(f"{k}: {v:.2f}" for k, v in sorted(tc.weights_l.items()))
        embed.add_field(name="L1-L5 Weights", value=w_text, inline=False)

        # Terms
        term_text = ", ".join(t.term for t in tc.terminology[:8])
        embed.add_field(name=f"Terminology ({len(tc.terminology)})", value=term_text or "—", inline=False)

        # Taboos
        taboo_text = "\n".join(f"[{t.severity}] {t.rule[:80]}" for t in tc.taboos[:3])
        embed.add_field(name=f"Taboos ({len(tc.taboos)})", value=taboo_text or "—", inline=False)

        embed.add_field(name="Pipeline", value=tc.pipeline.variant, inline=True)
        embed.set_footer(text="vulcaart.art")
        await interaction.response.send_message(embed=embed)

    # --- /vulca ask ---
    @tree.command(name="vulca-ask", description="Ask a cultural art question (powered by Gemini)")
    @app_commands.describe(question="Your question about cultural art")
    async def cmd_ask(interaction: discord.Interaction, question: str):
        await interaction.response.defer(thinking=True)

        answer = await _gemini_ask(question)

        embed = discord.Embed(
            title="CultureAdvisor",
            description=answer,
            color=0x8E8E93,
        )
        embed.set_footer(text=f"Q: {question[:100]}")
        await interaction.followup.send(embed=embed)

    # --- Bot startup ---
    @client.event
    async def on_ready():
        await tree.sync()
        logger.info("VULCA CultureAdvisor ready! Logged in as %s", client.user)
        print(f"VULCA CultureAdvisor ready! Logged in as {client.user}")

    return client


def main():
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN env var not set.")
        print("Create a bot at https://discord.com/developers and set the token.")
        return

    bot = build_bot()
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
