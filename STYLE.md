# Writing style for this book

Read this before writing or revising any chapter text. It adapts the guide
developed for the VEGFR R01 proposal (Sarabipour and Faeder, 2026) to a
textbook, and adds the checks from the `avoid-ai-writing` skill. Prose in a
recognizable LLM register reads as unedited and costs the reader's trust in
the science.

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
| 7 | Intensifiers ("exactly," "simply," "precisely," "worth noting," "powerful") | Delete, unless the word is literal ("must match exactly"). |
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
