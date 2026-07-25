"""Style profiles for concept-book content generation.

Each profile defines HOW verified content is written — tone, depth, audience,
structure — without changing WHAT is true.  The symbolic check
(graph_lib.verify_content) is style-agnostic; only the prose adapts.

A profile is resolved to a style_guide string by style_instruction(), which is
called via SOLVE in the SPL workflow and injected into every GENERATE prompt.

Identical copy of cookbook/73_intro_geometry/style_profiles.py's seven
profiles — the superset that adds ``middle_school``/``high_school`` to the
five recipe 71 originals. Recipe 74 compiles ONE source against whichever
@domain_yaml is resolved at runtime, so its style menu can't be tailored to
one domain's "natural" audience the way 71/73 each were; carrying the full
seven forward means every domain this recipe might load (linalg, geometry, or
a future one) gets the complete range a learner could plausibly want, rather
than a domain-specific subset baked in at compile time.
"""

from __future__ import annotations

STYLE_PROFILES: dict[str, dict[str, str]] = {
    "textbook": {
        "label": "University textbook",
        "tone": "precise and formal",
        "depth": "full definition, proof sketch, concrete worked example",
        "audience": "first-year university student with calculus background",
        "length": "300–400 words per section",
        "structure": "Definition → Worked example → Key theorem → Lab cell (SymPy)",
    },
    "feynman": {
        "label": "Feynman technique",
        "tone": "intuitive and story-driven; ask 'why does this feel right?' before formalising",
        "depth": "concept-first — build intuition, then let the algebra follow inevitably",
        "audience": "curious person comfortable with high-school algebra; no prior university math",
        "length": "200–300 words per section",
        "structure": "Motivating story → Intuition → Minimal formalisation → 'Now you try'",
    },
    "flashcard": {
        "label": "Anki flashcard set",
        "tone": "terse, precise, exam-ready",
        "depth": "one fact per card; no proofs, just the statement and one example",
        "audience": "student reviewing the night before an exam",
        "length": "50–100 words per section (one Q&A pair per key fact)",
        "structure": "Q: [precise question]  A: [minimal complete answer]  Example: [one line]",
    },
    "instructor": {
        "label": "Instructor teaching notes",
        "tone": "pedagogical; explicitly name common misconceptions and how to counter them",
        "depth": "concept summary + typical student errors + suggested in-class exercise",
        "audience": "instructor preparing a lecture or recitation",
        "length": "400–500 words per section",
        "structure": "Concept summary → Common mistakes → Teaching tip → Suggested exercise",
    },
    "research": {
        "label": "Research / reference",
        "tone": "dense and formal; theorem-proof style; citation-ready",
        "depth": "full proof, connection to standard references, remarks on generality",
        "audience": "graduate student or researcher who needs a precise, citable statement",
        "length": "200–300 words per section",
        "structure": "Definition → Theorem → Proof → Remark (connections / generalisations)",
    },
    "middle_school": {
        "label": "Middle school (grades 6–8)",
        "tone": "warm and encouraging; define every new term in plain words the moment it appears",
        "depth": "one idea at a time, concrete before abstract; heavy scaffolding, no formal proofs",
        "audience": "11-14 year old comfortable with arithmetic and pre-algebra, no calculus",
        "length": "150–250 words per section",
        "structure": "Everyday example → Picture this (visual description) → Simple rule → Try it yourself",
    },
    "high_school": {
        "label": "High school (grades 9–12)",
        "tone": "clear and motivating; build toward formal reasoning without losing the reader along the way",
        "depth": "definition, worked example, and a short 'why it's true' justification — first steps toward proof",
        "audience": "14-18 year old with an algebra 1 background, preparing for standardized tests (SAT/ACT)",
        "length": "250–350 words per section",
        "structure": "Real-world hook → Definition → Worked example → Why it's true → Practice problem",
    },
}


def get_style_profile(style: str) -> dict[str, str]:
    """Return the profile dict for the named style.

    Raises ValueError for unknown style names.
    """
    profile = STYLE_PROFILES.get(style)
    if profile is None:
        available = ", ".join(f"'{s}'" for s in STYLE_PROFILES)
        raise ValueError(f"Unknown style: {style!r}. Available: {available}")
    return profile


def style_instruction(style: str) -> str:
    """Return a prose instruction block for injecting into LLM prompts.

    Called via SOLVE @style_guide TEXT := style_instruction(@style) in the
    SPL workflow.  The returned string is passed as {style_guide} into every
    GENERATE prompt template so the LLM writes in the chosen style.
    """
    p = get_style_profile(style)
    return (
        f"STYLE GUIDE — {p['label']}\n"
        f"Tone      : {p['tone']}\n"
        f"Depth     : {p['depth']}\n"
        f"Audience  : {p['audience']}\n"
        f"Length    : {p['length']}\n"
        f"Structure : {p['structure']}"
    )


def available_styles() -> list[str]:
    """Return the list of supported style names."""
    return list(STYLE_PROFILES.keys())


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for name in STYLE_PROFILES:
        print(f"\n{'='*60}")
        print(style_instruction(name))
