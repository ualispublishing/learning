#!/usr/bin/env python3
"""Reviewed semantic overrides for French/Urdu core candidates.

This layer is used only after multi-source audit has isolated rows whose automatic
or dictionary-selected gloss is ambiguous, overly technical, archaic, or the wrong
homograph for a learner deck. Entries here have been explicitly reviewed.
"""
import refine_french_urdu_candidate_meanings as base

base.FRENCH_SAFE.update({
    "cette": "this; that (feminine singular)",
    "des": "of the; from the; some (plural partitive/indefinite article)",
    "ses": "his; her; its (before a plural noun)",
    "mieux": "better",
    "tes": "your (informal singular possessor; before a plural noun)",
    "fait": "fact; deed; event; done; made",
    "cet": "this; that (masculine singular before a vowel or mute h)",
    "désoler": "to sadden; distress; upset",
    "désolé": "sorry; saddened; desolate",
    "eh": "eh; hey; huh (interjection)",
    "quelle": "which; what (feminine singular)",
    "hé": "hey!; ho! (interjection)",
    "pendant": "during; for (a duration); while",
    "hein": "huh?; right?; isn't it?",
    "rappeler": "to remind; recall; call back",
    "ni": "neither; nor",
    "aucune": "no; none; not any (feminine)",
    "euh": "um; uh (hesitation)",
    "super": "great; super; fantastic",
    "boulot": "job; work (informal)",
    "celui": "the one; that one (masculine singular)",
    "tour": "turn; round; tour; tower",
    "l'un": "one; one of them",
    "tiens": "here; look; hey; hold! (form of tenir)",
    "dès": "from; as early as; as soon as",
    "toute": "all; every; whole (feminine singular)",
    "sinon": "otherwise; if not; except",
    "pote": "friend; buddy; mate (informal)",
    "rejoindre": "to join; rejoin; reach; catch up with",
    "sympa": "nice; friendly; pleasant (informal)",
    "ficher": "to file; put/stick; not care (se ficher de, informal)",
    "virer": "to fire/dismiss; turn; remove; transfer (informal senses vary)",
    "censé": "supposed to; meant to",
    "tueur": "killer; murderer",
    "arrière": "rear; back; behind",
    "gosse": "kid; child (informal)",
    "laquelle": "which one; which (feminine singular)",
    "doucement": "gently; softly; slowly; quietly",
    "travers": "fault; defect; crosswise; through/across (in à travers)",
    "moi-même": "myself",
    "horrible": "horrible; awful",
    "excellent": "excellent; great",
    "bosser": "to work (informal); emboss/dent",
    "connerie": "bullshit; stupidity; stupid thing (vulgar)",
    "filer": "to spin/thread; slip away; give/pass; tail/follow",
    "là-dedans": "in there; in that",
    "forcer": "to force; compel; make",
    "hum": "hmm; um",
    "lequel": "which one; which (masculine singular)",
    "nulle": "no; none (feminine); lousy/terrible (informal adjective)",
    "soit": "either; be (subjunctive of être); namely/that is; okay/agreed",
})

# Additional Urdu reviewed overrides are appended by the final Urdu discrepancy pass.

if __name__ == "__main__":
    base.main()
