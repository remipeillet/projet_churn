from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

SECONDAIRE = "#eb6834"
BLEU_CLAIR = "#dce9f9"
ORANGE_CLAIR = "#fbe3d8"

fig, ax = plt.subplots(figsize=(12.5, 7.2))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
ax.set_xlim(0, 1.0); ax.set_ylim(0, 1); ax.axis("off")


def bloc(x, y, w, h, titre, lignes=(), fond=SURFACE, bord=CONTEXTE, encre=INK, encre2=INK_2, gras=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012",
                                facecolor=fond, edgecolor=bord, linewidth=1.6, zorder=2))
    haut = y + h - 0.045 if lignes else y + h / 2
    ax.text(x + w / 2, haut, titre, ha="center", va="center" if not lignes else "top",
            fontsize=10.5, fontweight="bold" if gras else "normal", color=encre, zorder=3)
    for k, ligne in enumerate(lignes):
        ax.text(x + w / 2, y + h - 0.082 - 0.038 * k, ligne, ha="center", va="top",
                fontsize=8.8, color=encre2, zorder=3)


def fleche(depart, arrivee, couleur=INK_2, style="arc3,rad=0", trait=1.6, pointille=False):
    ax.add_patch(FancyArrowPatch(depart, arrivee, connectionstyle=style, arrowstyle="-|>",
                                 mutation_scale=13, linewidth=trait, color=couleur,
                                 linestyle=(0, (4, 3)) if pointille else "solid", zorder=1))


# --- Rangee 1 : la chaine de scoring ----------------------------------------
bloc(0.02, 0.70, 0.26, 0.26, "Systèmes sources",
     ("Produit — usage, connexions", "Facturation — MRR, retards",
      "Support — tickets, délais", "CRM — comptes, contrats",
      "Catalogue des plans"), fond="#f2f1ec")
bloc(0.36, 0.70, 0.26, 0.26, "Préparation",
     ("parsing, normalisation,", "jointure catalogue,", "ratios métier", "code versionné (§7)"),
     fond=BLEU_CLAIR, bord=ACCENT)
bloc(0.68, 0.70, 0.225, 0.26, "Modèle sérialisé",
     ("pipeline complet", "+ manifeste : version,", "seuil, colonnes attendues", "(§10.1)"),
     fond=BLEU_CLAIR, bord=ACCENT)

fleche((0.285, 0.83), (0.355, 0.83))
fleche((0.625, 0.83), (0.675, 0.83))
ax.text(0.32, 0.865, "extraction\nmensuelle", ha="center", va="bottom", fontsize=8.2, color=INK_2)

# --- Table de scores ---------------------------------------------------------
bloc(0.28, 0.44, 0.44, 0.17, "TABLE DE SCORES  ·  historisée",
     ("compte · probabilité · rang · facteurs explicatifs",
      "version du modèle · seuil appliqué · date du cycle"),
     fond=ACCENT, bord=ACCENT, encre="#ffffff", encre2="#eaf2fd")
fleche((0.79, 0.695), (0.60, 0.615), style="arc3,rad=-0.18", couleur=ACCENT)

# --- Trois circuits ----------------------------------------------------------
bloc(0.02, 0.19, 0.28, 0.17, "Circuit opérationnel",
     ("CRM — fiche compte", "liste priorisée remise aux CSM"), fond=BLEU_CLAIR, bord=ACCENT)
bloc(0.36, 0.19, 0.28, 0.17, "Circuit de mesure",
     ("groupe témoin (5–10 %)", "scoré mais NON restitué"), fond=ORANGE_CLAIR, bord=SECONDAIRE)
bloc(0.68, 0.19, 0.225, 0.17, "Supervision",
     ("dérive · équité par segment", "contrôle d'AUC univariée"), fond=ORANGE_CLAIR, bord=SECONDAIRE)

fleche((0.42, 0.435), (0.18, 0.365), style="arc3,rad=0.12", couleur=ACCENT)
fleche((0.50, 0.435), (0.50, 0.365), couleur=SECONDAIRE)
fleche((0.58, 0.435), (0.79, 0.365), style="arc3,rad=-0.12", couleur=SECONDAIRE)

# --- Boucle d'amelioration ---------------------------------------------------
bloc(0.02, 0.02, 0.28, 0.11, "Actions CSM tracées",
     ("date · type · issue",), fond=SURFACE, bord=CONTEXTE)
bloc(0.60, 0.02, 0.305, 0.11, "Ré-entraînement (§13.2)",
     ("sur labels non contaminés",), fond=ORANGE_CLAIR, bord=SECONDAIRE)

fleche((0.16, 0.185), (0.16, 0.135), couleur=INK_2)
fleche((0.305, 0.075), (0.595, 0.075), couleur=SECONDAIRE)
fleche((0.50, 0.185), (0.50, 0.105), couleur=SECONDAIRE, style="arc3,rad=0")
fleche((0.79, 0.185), (0.79, 0.135), couleur=SECONDAIRE)
fleche((0.938, 0.075), (0.912, 0.80), style="angle,angleA=0,angleB=-90,rad=12", couleur=SECONDAIRE, pointille=True)
ax.text(0.988, 0.42, "nouvelle version du modèle", rotation=90, ha="center", va="center",
        fontsize=8.4, color=SECONDAIRE, fontweight="bold")

ax.set_title("Architecture cible — un scoring batch mensuel, trois circuits d'usage",
             loc="left", fontsize=13, fontweight="bold", color=INK, pad=14)
plt.tight_layout()
plt.savefig("/tmp/claude-1000/-home-remi-workspace-ml-projet-churm/511bcd10-b7f8-4571-bd34-dcbe74ae6798/scratchpad/schema.png",
            dpi=110, bbox_inches="tight")
print("ok")
