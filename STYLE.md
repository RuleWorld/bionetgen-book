# Writing style for this book

Read this before writing or revising any chapter text. It adapts the guide
developed for the VEGFR R01 proposal (Sarabipour and Faeder, 2026) to a
textbook, and adds the checks from the `avoid-ai-writing` skill. Prose in a
recognizable LLM register reads as unedited and costs the reader's trust in
the science.

## Voice: write the way Jim Faeder writes

The book should sound like its author. The models for this voice are his
single-author paper (Faeder, *J. Chem. Phys.* **99**, 7664, 1993) and the
introduction to his thesis (*The X₂⁻ Files*, University of Colorado, 1998). His
later first-author papers (*J. Immunol.* 2003; *Methods Mol. Biol.* 2009) are
secondary models. A comparison on 2026-10-10 found that the drafts matched his
sentence length (about 30 words on average) but not the way his sentences
connect. The patterns below come from those texts. The quoted sentences are his.

1. **Set up a concept with "Consider…".**
   - "Consider the case of an atom-molecule complex."
   - "Consider a molecule with two electronic states."

   Introduce a thought experiment, then follow its consequences step by step.
2. **Tell history through people.**
   - "The recombination of photodissociated I₂ in solution was first observed in
     the early 1930's by Franck and Rabinowitch, who called this process the
     'cage effect.' Later, Noyes and coworkers carried out systematic
     studies…"

   When a concept has a history (mass action, the stochastic simulation
   algorithm, rule-based modeling), name who found it and what they saw.
3. **Distinguish expectation from result.** Use calibrated modals for
   expectations: "should be more efficient," "one would expect," "it might be
   possible," "seems to account for." Use plain declaratives for what a
   calculation shows. Say so when something is not understood: "No explanation
   for this observation is immediately evident."
4. **Let lead-in clauses carry the logic.**
   - "Given the relatively large reduced mass of the complex…, one expects…"
   - "Provided that r_cutoff is chosen reasonably small, this damping should not
     have any physical consequence…"
   - "Using the adiabatic states as a basis, we can determine…"
5. **Explain the mechanism behind a result.**
   - "This is because overall rotation about the intermolecular axis may cancel
     the angular momentum contribution…"
6. **Connect with "thus," mid-sentence "however," and "since."** Prefer these
   over chains of "because." Use "For example," often.
7. **Walk through a figure with physical verbs.**
   - "Following excitation to a repulsive state, the iodine atoms fly apart and
     begin to encounter the surrounding atoms. In some cases… In other
     cases…"
8. **State findings plainly.**
   - "The data impose severe constraints on the parameters."

   Short declaratives that carry a finding are part of the voice. Short
   sentences that only add drama are not.
9. **Close a line of argument with its implication.**
   - "These results demonstrate the possible pitfalls in attempting to label
     experimentally observed bands with vibrational mode quantum numbers…"
   - "This discussion demonstrates the need for a sophisticated model…"
10. **Use a light personal touch in framing passages only.** Examples are the
    thesis title and "a low-level conspiracy to deny it funding." Occasional
    humor belongs in the preface and chapter openings, not in explanations.
11. **Signpost structure.**
    - "The remainder of this chapter provides greater context…"
    - "As mentioned above…"
12. **Some phrases that the AI-writing checklists flag are part of this voice**:
    "It is important to note that," "It is interesting to note that," and
    "worthy of note." Keep them, but use at most one per section, and only
    where the noted point is a real caveat or surprise.

"We" is the reasoning voice ("we may predict," "we wish to use"). Passive voice
is acceptable for procedures ("Calculations were performed…"), as in the
sources. "I" appears only in the preface.

## Register

- **Explanatory and declarative.** State the content; do not set it up first.
  A textbook can use shorter sentences than a proposal, but each sentence must
  carry content. Sentence length should follow the logic, not a rhythm.
- **Plain verbs**: "binds," "generates," "we simulate," "the model predicts."
- **Every claim carries a specific**: a number, a molecule, a method, a figure,
  or a citation. Numbers in the text come from running the book's models, or
  from a cited source.
- **Bold marks a term at its definition**, and nothing else. Do not bold for
  emphasis, in learning-goal lists, or in summaries.
- **Address the reader as "we"** when working through a model, and "you" for
  instructions ("Call `model.reset()` before each run").

## Constructions to avoid

From the R01 `STYLE.md` table, the tells that apply to textbook prose:

| # | Avoid | Write instead |
|---|---|---|
| 1 | Short punch sentence after a long one ("That worked for twelve species.") | Fold it into the neighboring sentence as a clause. |
| 2 | Verbless contrastive fragment | A full sentence. |
| 3 | "not X; it is Y" / "X, not Y" / tailing negation ("…, it doesn't matter what") | State the positive claim. |
| 4 | Em-dash aside for emphasis | Comma, semicolon, parentheses, or a new sentence. |
| 5 | Colon as dramatic reveal ("Real networks cannot: their equations are…") | A conjunction ("because," "so," "but"), a semicolon, or two sentences. A colon introducing a list, a code block, or a displayed equation is fine. |
| 6 | Meta-commentary on the text ("Two details deserve attention," "The value of rules becomes clear when…," "the main idea of the whole book") | Delete; state the content. |
| 7 | Intensifiers ("exactly," "simply," "precisely," "powerful") | Delete, unless the word is literal ("must match exactly"). See Voice item 12 for the "It is important to note" exception. |
| 8 | Sentence-initial And / But / Yet for punch | "In addition," "However," or merge. |
| 9 | Idiomatic flourishes | The literal statement. |
| 10 | Triads for rhythm ("large, interconnected, and full of feedback") | As many items as the content has. |
| 11 | Rhetorical questions as transitions | A statement of the open question. Section headings may be questions. |
| 13 | Unresolved demonstrative at the start of a paragraph or caption ("This is…") | Name the referent. |
| 14 | Overloaded compound sentence chaining several results | One claim per sentence. |
| 15 | Consecutive sentences ending on the same weak pronoun ("…it." "…it.") | Name the thing. |

From the `avoid-ai-writing` skill catalog, also watch for:

- the Tier 1 vocabulary (delve, leverage, robust, comprehensive, pivotal,
  seamless, landscape, crucial, and the rest);
- significance inflation;
- "serves as" or "features" in place of "is" or "has";
- vague attributions ("studies show") without a citation;
- generic closing sentences.

## Checks before committing a chapter

1. Read the prose against the table above.
2. Run the detector on the chapter's prose (code, equations, and tables
   removed):

   ```bash
   node ~/.claude/skills/avoid-ai-writing/bin/avoid-ai-writing.js --context technical prose.md
   ```

3. After an editing pass, confirm that no numbers, citations, or code changed:

   ```bash
   node ~/.claude/skills/avoid-ai-writing/detector/validate.js --residual-policy warn before.md after.md
   ```

4. Run `quarto render` and confirm that it reports no warnings.
