# bg3-mod-translator
This tool automates XML localization using the OpenAI API and a local translation memory:

Language Selection
Specify source and target codes (e.g. en → pt-BR).

XML Parsing
Read each <content> block’s contentUid, version and text.

Translation Memory Lookup

If the source text exists in your database for the target language, reuse its translation.

Otherwise, use RapidFuzz to find the top‑5 closest matches from your DB and include them as context in a custom prompt to OpenAI.

API Request
Send the prompt to OpenAI and retrieve the translated text.

Output Generation

Recreate the original folder structure.

Write the translated localization.xml.

Generate meta.xlsx with contentUid, version and description, properly versioned.

This prototype can be extended into a Django + Vue.js web app to support more file types and dynamic language pairs.
