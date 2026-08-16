#!/usr/bin/env python3
"""Retry Unit 08 with exact infinitive `douter` visible in the checkpoint."""
from __future__ import annotations
import generate_french_a2_unit08 as base

base.CHECKPOINT["text"]="""Quand Camille reçoit une information incertaine, elle évite de deviner trop vite. Si quelque chose paraît étrange, elle peut demander de répéter le message et observer un signe utile. Pour savoir à qui un objet peut appartenir, elle cherche un indice puis confirme son idée. Lorsqu’une classe doit choisir entre plusieurs services, elle vérifie le nom de la compagnie avant d’avancer. Si elle commence à douter d’une affirmation simple, un test peut parfois apporter une réponse concrète. Camille apprend aussi que la parole aide à comprendre le but d’un projet : devant un mur qui suscite son intérêt, écouter les personnes concernées ajoute du contexte. Ces habitudes restent utiles pendant un déjeuner partagé, une sortie avec une belle vue ou une course entre le marché et la poste. Camille comprend finalement qu’une bonne décision repose rarement sur un seul détail. Elle rassemble plusieurs éléments, pose une question précise et accepte de corriger sa première impression quand les signes montrent autre chose."""

base.main()
