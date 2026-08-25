#!/usr/bin/env python3
"""Source-backed pronunciation foundations for the v1 language workbooks.

The goal is beginner support without unreliable per-sentence romanization. The
workbooks teach a compact broad-IPA/articulation key in Foundations and continue
to present vocabulary and sentence drills in normal target-language spelling.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

import build_language_workbooks_v1 as base

ORIGINAL_FOUNDATIONS_HTML = base.foundations_html
ARABIC_RUN = re.compile(r"([\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+)")

PRONUNCIATION = {
    "arabic": {
        "scope": "Broad Modern Standard Arabic (MSA) reference pronunciation. Educated formal speech varies regionally, especially for a few consonants, so the guide marks stable contrasts and notes major variation instead of pretending there is one accent-free phonetic realization.",
        "rows": [
            ("Vowel length", "/a i u/ versus /aː iː uː/", "Length is contrastive. A long vowel is not merely a more strongly stressed short vowel; sustain the vowel for longer while keeping its target quality."),
            ("Emphatic consonants", "ص /sˤ/ · ض /dˤ/ · ط /tˤ/ · ظ /ðˤ/", "These have secondary pharyngealization and can back nearby vowels. The careful MSA target for ظ is /ðˤ/, while regional realizations may differ."),
            ("Pharyngeals", "ح /ħ/ · ع /ʕ/", "Keep ح distinct from ه /h/, and ع distinct from a vowel onset or ء /ʔ/. These sounds are formed with constriction in the pharyngeal region."),
            ("Dorsal fricatives", "خ /x~χ/ · غ /ɣ~ʁ/", "Use a fricative made far back in the mouth; exact velar/uvular realization varies without changing the spelling."),
            ("Qaf and hamza", "ق /q/ · ء /ʔ/", "These are broad careful MSA reference targets. Speakers may carry regional realizations into formal speech, so recognize variation without changing the written form."),
            ("Gemination", "shadda ّ = consonant length", "A consonant with shadda is held longer than its singleton counterpart. Consonant length can distinguish lexical or grammatical forms."),
            ("Sun-letter assimilation", "ال + sun letter", "Before a sun letter, the /l/ of the definite article assimilates in pronunciation and the following consonant is geminated; the spelling still keeps ال."),
            ("Short-vowel marks", "fatḥa /a/ · kasra /i/ · ḍamma /u/", "Short-vowel diacritics are useful pronunciation aids but are commonly omitted in ordinary Arabic text. Learn the word form rather than guessing a short vowel from bare consonantal spelling."),
        ],
        "practice": [
            "First identify vowel length, emphatic/pharyngeal consonants, and any shadda before trying to read the whole word.",
            "Read once slowly with those contrasts exaggerated slightly, then repeat at normal speed without changing the contrasts.",
            "Treat the IPA here as a broad reference. For a new word whose vowels are not written, confirm the lexical pronunciation before drilling it repeatedly.",
        ],
        "sources": [
            "Standard Arabic phonology (reference overview; cites Cambridge and specialist phonological sources)",
            "Karin C. Ryding, A Reference Grammar of Modern Standard Arabic, Cambridge University Press",
        ],
    },
    "french": {
        "scope": "Broad contemporary standard/Metropolitan French reference pronunciation. The guide highlights contrasts that commonly cause beginner errors and explicitly marks features that vary by region, register, or speech rate.",
        "rows": [
            ("u versus ou", "u /y/ · ou /u/", "Keep these vowels distinct. For /y/, hold the tongue near the position for /i/ while rounding the lips; /u/ is a back rounded vowel."),
            ("Nasal vowels", "sans /sɑ̃/ · son /sɔ̃/ · pain /pɛ̃/ · un /œ̃/", "These are broad reference examples. Many speakers merge /œ̃/ with /ɛ̃/, and spelling-to-sound patterns have lexical exceptions, so do not generalize from letters alone."),
            ("French r", "r /ʁ/", "A common standard reference target is uvular. Its exact phonetic realization can range from approximant-like to fricative or trill-like across speakers and contexts."),
            ("Schwa", "e /ə/ in some contexts", "Schwa may be pronounced or omitted depending on the word, rhythm, register, and surrounding sounds. Not every written e represents /ə/."),
            ("Word-final consonants", "often silent, but lexical", "Many final consonant letters are not pronounced, but there are important word-specific exceptions. Learn the pronunciation with the lexical item instead of applying a blanket deletion rule."),
            ("Liaison", "latent final consonant + following vowel sound", "In appropriate grammatical contexts a normally silent final consonant can surface before a following vowel sound. Liaison can be obligatory, optional, or forbidden; it is not triggered mechanically before every vowel-initial word."),
            ("Elision", "j’aime · l’ami", "Certain short function words lose a final vowel before a following vowel sound or mute h, and the apostrophe marks the elision in writing."),
            ("Rhythm", "phrase/rhythm-group prominence", "French does not use English-style fixed lexical stress on each content word. Prominence tends to fall near the end of a rhythm group, with phrasing and speech style affecting the result."),
        ],
        "practice": [
            "Mark /y/ versus /u/, nasal vowels, and any liaison or elision before reading a phrase aloud.",
            "Read in short rhythm groups rather than stressing each content word as though it were English.",
            "Use the IPA as a broad target and confirm unfamiliar lexical exceptions rather than inventing pronunciations from spelling alone.",
        ],
        "sources": [
            "French phonology (reference overview of contemporary vowel/consonant systems and variation)",
            "French liaison (reference overview distinguishing obligatory, optional, and forbidden liaison)",
        ],
    },
    "urdu": {
        "scope": "Broad standard Urdu pronunciation in Nastaliq. The guide prioritizes contrasts that the script can obscure for beginners, especially dental/retroflex place, aspiration, vowel length/quality, and nasalization.",
        "rows": [
            ("Dental versus retroflex", "ت /t̪/ · د /d̪/ versus ٹ /ʈ/ · ڈ /ɖ/ · ڑ /ɽ/", "Keep tongue placement distinct: dental stops contact the teeth; retroflex sounds use a retracted or curled tongue-tip gesture."),
            ("Aspiration", "پ /p/ versus پھ /pʰ/ · ک /k/ versus کھ /kʰ/", "Aspiration is contrastive. In aspirated digraphs, do-chashmi he ھ marks the aspirated series; do not pronounce it as a separate extra syllable."),
            ("Short and long vowels", "short-vowel series versus long-vowel series", "Vowel length and quality can distinguish words. Short vowels are often not written, while long vowels are more often represented with ا، و، ی/ے and related orthographic patterns."),
            ("Nasalization", "word-final ں = nūn ghunnah", "Word-final ں commonly marks nasalization of the preceding vowel rather than a full oral /n/. Medial nasalization uses different orthographic conventions and must be read in context."),
            ("ہ versus ھ", "ہ /h/ or orthographic element · ھ aspiration marker", "Gol he ہ and do-chashmi he ھ have different roles. The latter normally participates in aspirated consonant digraphs."),
            ("Perso-Arabic loan consonants", "ق /q/ · خ /x/ · غ /ɣ/ · ف /f/ · ژ /ʒ/", "Careful standard speech can distinguish these sounds, while some speakers merge particular loan phonemes with more common sounds. Recognize both the careful target and normal speaker variation."),
            ("و and ی", "و may be consonantal /ʋ~w/ or part of a vowel spelling; ی may be /j/ or part of a vowel spelling", "These letters are multifunctional, so their pronunciation must be interpreted from the word rather than assigned one fixed sound."),
            ("Stress", "not marked in ordinary spelling", "Urdu stress is not written directly and depends on phonological structure. For beginners, preserve consonant place, aspiration, vowel contrasts, and nasalization first, then refine stress with reliable native audio."),
        ],
        "practice": [
            "Before reading, mark any retroflex letter, aspirated digraph, long-vowel spelling, or nūn ghunnah.",
            "Say dental/retroflex and aspirated/unaspirated pairs deliberately enough that the contrast survives when you speed up.",
            "Because ordinary Urdu omits many short-vowel cues, confirm unfamiliar words before drilling them repeatedly instead of guessing from consonantal spelling alone.",
        ],
        "sources": [
            "Urdu phonology (reference overview; includes consonant and vowel inventories and cites CRULP phonetic work)",
            "Center for Research in Urdu Language Processing: Urdu consonantal and vocalic sounds",
            "Omniglot Urdu alphabet reference for Nastaliq, nūn ghunnah, and aspirated-letter conventions",
        ],
    },
}


def _pron_target_html(lang: str, cfg: dict, target: str) -> str:
    """Render mixed Arabic-script + IPA/Latin content without bidi reordering.

    Pronunciation examples are pedagogical pairs, not target-language prose. Keep
    the row itself LTR so its authored sequence is stable, and isolate each
    Arabic-script run in an RTL BDI span using the language font.
    """
    if cfg["dir"] != "rtl":
        return (
            '<div class="target" dir="ltr" '
            f'style="--target-font:\'{cfg["font"]}\';text-align:left">'
            f'{base.esc(target)}</div>'
        )

    rendered = []
    for part in ARABIC_RUN.split(target):
        if not part:
            continue
        if ARABIC_RUN.fullmatch(part):
            rendered.append(
                '<bdi dir="rtl" '
                f'style="font-family:\'{cfg["font"]}\';font-size:1.18em">'
                f'{base.esc(part)}</bdi>'
            )
        else:
            rendered.append(f'<bdi dir="ltr">{base.esc(part)}</bdi>')
    return (
        '<div dir="ltr" style="font-family:\'DejaVu Sans\',sans-serif;'
        'font-size:15pt;font-weight:600;line-height:1.5;margin:.05in 0 .08in;'
        'text-align:left;unicode-bidi:isolate">'
        + "".join(rendered)
        + '</div>'
    )


def _guide_html(lang: str, cfg: dict) -> str:
    guide = PRONUNCIATION[lang]
    cards = []
    for title, target, note in guide["rows"]:
        cards.append(
            '<div class="foundation-card">'
            f'<h3>{base.esc(title)}</h3>'
            f'{_pron_target_html(lang, cfg, target)}'
            f'<p>{base.esc(note)}</p>'
            '</div>'
        )
    habits = "".join(f"<li>{base.esc(x)}</li>" for x in guide["practice"])
    return (
        '<h2>Pronunciation quick-start</h2>'
        f'<p class="note">{base.esc(guide["scope"])}</p>'
        '<p class="note"><strong>Notation:</strong> slashes / / show broad IPA phonemes or practical reference targets. '
        'They are more precise than English respellings but still do not encode every accent or connected-speech detail.</p>'
        + "".join(cards)
        + '<div class="foundation-card"><h3>Three-step pronunciation routine</h3>'
        f'<ol>{habits}</ol></div>'
        '<p class="note">Sentence drills intentionally stay in normal target-language spelling: the pronunciation key supports decoding without creating dependence on ad-hoc romanization.</p>'
    )


def foundations_html(lang: str, cfg: dict) -> str:
    original = ORIGINAL_FOUNDATIONS_HTML(lang, cfg)
    marker = "</section>"
    if not original.endswith(marker):
        raise RuntimeError("unexpected foundations HTML shape; refusing unsafe pronunciation injection")
    return original[:-len(marker)] + _guide_html(lang, cfg) + marker


def cover(cfg: dict, segment: str) -> str:
    # Import lazily to avoid coupling this module to quality-builder import order.
    import build_language_workbooks_v1_quality as quality

    html = quality.quality_cover(cfg, segment)
    html = html.replace(
        "Writing foundations, core grammar, 1,000 audited vocabulary entries, and 1,000 curated bilingual practice sentences with handwriting and retrieval space.",
        "Writing and pronunciation foundations, core grammar, 1,000 audited vocabulary entries, and 1,000 curated bilingual practice sentences with handwriting and retrieval space.",
    )
    html = html.replace(
        "Transliteration is intentionally omitted from sentence drills rather than teaching inconsistent ad-hoc romanization.",
        "A source-backed pronunciation key is taught in Foundations; sentence drills then use normal target-language spelling rather than inconsistent ad-hoc romanization.",
    )
    return html


def audit_payload() -> dict:
    required = {"arabic", "french", "urdu"}
    if set(PRONUNCIATION) != required:
        raise SystemExit("pronunciation guide language set mismatch")

    for lang, guide in PRONUNCIATION.items():
        if len(guide["rows"]) < 8:
            raise SystemExit(f"{lang}: pronunciation guide must contain at least 8 reviewed contrast/rule cards")
        if len(guide["practice"]) != 3:
            raise SystemExit(f"{lang}: pronunciation routine must contain exactly 3 steps")
        if len(guide["sources"]) < 2:
            raise SystemExit(f"{lang}: pronunciation guide needs at least two reference sources")
        joined = json.dumps(guide, ensure_ascii=False).casefold()
        if "sounds like" in joined or "rhymes with" in joined:
            raise SystemExit(f"{lang}: ambiguous English-respelling shortcut found")
        if "romanization:" in joined or "transliteration:" in joined:
            raise SystemExit(f"{lang}: per-item romanization/transliteration field found")

    for lang in ("arabic", "urdu"):
        cfg = base.LANGS[lang]
        rendered = "\n".join(_pron_target_html(lang, cfg, row[1]) for row in PRONUNCIATION[lang]["rows"])
        if '<div dir="ltr"' not in rendered or '<bdi dir="rtl"' not in rendered or '<bdi dir="ltr"' not in rendered:
            raise SystemExit(f"{lang}: mixed-direction pronunciation isolation gate failed")
        if 'class="target rtl"' in rendered:
            raise SystemExit(f"{lang}: pronunciation rows must not inherit paragraph-level RTL direction")

    canonical = json.dumps(PRONUNCIATION, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "status": "PASS",
        "scope": "beginner pronunciation foundations",
        "languages": sorted(required),
        "guide_sha256": digest,
        "checks": {
            "all_languages_present": True,
            "minimum_reviewed_cards_per_language": 8,
            "three_step_practice_routine": True,
            "broad_ipa_not_english_respelling": True,
            "no_per_sentence_romanization_dependency": True,
            "source_notes_present": True,
            "mixed_direction_ipa_isolated": True,
        },
        "assurance_note": "No known pronunciation-guide defect after source-backed review. This gate validates the workbook guide and its pedagogical constraints; it is not a substitute for native-audio evaluation of every possible accent realization.",
        "sources": {lang: PRONUNCIATION[lang]["sources"] for lang in sorted(required)},
    }


def write_qa() -> dict:
    payload = audit_payload()
    payload["generated_utc"] = datetime.now(timezone.utc).isoformat()
    path = base.AUDIT / "pronunciation_qa.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
