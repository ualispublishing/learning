#!/usr/bin/env python3
"""Run hardened French A2 Unit 01 with exact visible A1 bridge reviews."""
from __future__ import annotations

import re
import generate_french_a2_unit01_retry as retry

ACCEPTED_A1_BLOB = "0493a2fa13e51b5997db05e91cdea4d8dc5e647b"
_original_loader = retry.load_base_namespace

BRIDGE_SENTENCES = {
    "ciel": "Le ciel est clair ce matin.",
    "soleil": "Le soleil commence à se lever.",
    "froid": "Dehors, il fait encore froid.",
    "chaud": "Dans le bureau, il fait chaud.",
    "acheter": "Camille veut acheter son billet ici.",
    "prix": "Le prix reste affiché à l’écran.",
    "argent": "Elle vérifie aussi l’argent qu’elle a avec elle.",
    "vêtement": "Elle pensait acheter un vêtement après les cours.",
    "sac": "Elle pose son sac sous la chaise.",
    "chaussure": "Elle remet correctement sa chaussure avant d’entrer.",
}


def exact_count(text: str, form: str) -> int:
    return len(re.findall(rf"(?<!\w){re.escape(form)}(?!\w)", text, flags=re.I | re.UNICODE))


def load_closed_a1_base():
    ns = _original_loader()
    ns["EXPECTED_A1_BLOB"] = ACCEPTED_A1_BLOB
    original_main = ns["main"]

    def main_with_visible_bridges():
        data = ns["DATA"]
        added = []
        for spec in data["specs"]:
            missing = [f for f in spec.get("reviews", []) if exact_count(spec["text"], f) < 1]
            if missing:
                sentences = []
                for form in missing:
                    if form not in BRIDGE_SENTENCES:
                        raise AssertionError(f"no natural bridge sentence configured for {spec['pid']}:{form}")
                    sentences.append(BRIDGE_SENTENCES[form])
                    added.append(f"{spec['pid']}:{form}")
                spec["text"] = spec["text"].rstrip() + " " + " ".join(sentences)
        # Recheck before the canonical generator's own strict visibility gate.
        for spec in data["specs"]:
            for form in spec.get("reviews", []):
                if exact_count(spec["text"], form) < 1:
                    raise AssertionError(f"bridge visibility repair failed for {spec['pid']}:{form}")
        print({"bridge_review_sentences_added": added})
        return original_main()

    ns["main"] = main_with_visible_bridges
    return ns


retry.load_base_namespace = load_closed_a1_base

if __name__ == "__main__":
    retry.main()
