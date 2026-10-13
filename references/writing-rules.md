# Clear Answer rules

The rules that the linter (`scripts/ste_lint.py`) checks. They are a
machine-checkable part of ASD-STE100 Simplified Technical English, plus some chat
style rules.

`passed` is true when there is no **error**. Warnings do not stop the answer, but
fix them when you can.

## Errors

| Rule | Prose (chat) | Strict (full) | Notes |
|---|---|---|---|
| sentence-length | 25 words or fewer | 20 words or fewer | STE: procedures 20, descriptions 25 |
| paragraph-length | 6 sentences or fewer | 6 sentences or fewer | one topic for each paragraph |
| semicolon | not allowed | not allowed | write two sentences |
| contraction | not allowed | not allowed | write "do not", not "don't" |
| progressive-tense | not allowed | not allowed | "is running" |
| perfect-tense | not allowed | not allowed | "has done" |
| unclosed-code-fence | not allowed | not allowed | the text after it is not checked |

## Warnings

| Rule | Notes |
|---|---|
| passive-voice | do not use it in instructions |
| phrasal-verb | use one verb: "remove", not "take off" |
| one-instruction | do not join two commands with "and" or "then" |
| unapproved-word | a word that STE does not approve for this part of speech, with the approved options |
| wordiness | a wordy phrase, such as "in order to" |
| removed-word | a word that Issue 9 removed from the word list |

Chat style warnings, in prose mode only. They are not STE rules:

| Rule | Check |
|---|---|
| bold-overuse | more than 2 bold spans in a reply |
| header-in-short-reply | a header in a reply of fewer than 150 words |
| bullet-overuse | a bullet list of 1 item, or of more than 7 items |
| filler-opener | an opener such as "Great question" |
| filler-closer | a closer such as "I hope this helps" |

## How the linter reads text

- Code blocks, inline code, HTML tags, and quote markers are not checked as
  text.
- Each list item and each table cell is checked on its own.
- A sentence ends at ".", "!", or "?" followed by a space, so "example.com" stays
  inside its sentence.
- Words are checked by their part of speech in the sentence. "file (v)" warns on
  "file the edge" but not on "open the file".

## Word lists

The linter merges three layers, and a later layer wins:

1. the built-in list in `scripts/ste_dictionary.py`,
2. your imported official dictionary in `cache/official.json`,
3. a `.ste-dict.txt` file in the working folder.

## Not checked

- The meaning of a word. STE gives each approved word one meaning.
- Groups of more than three nouns.
- Whether a text is a procedure or a description. Choose the profile yourself.
- One topic for each paragraph.

## References

- ASD-Europe (official): https://www.asd-europe.org/standards-specifications/simplified-technical-english/
- ASD-STE100 home: https://www.asd-ste100.org/
- Wikipedia overview: https://en.wikipedia.org/wiki/Simplified_Technical_English
