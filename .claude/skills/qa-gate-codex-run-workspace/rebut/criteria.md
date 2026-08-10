slugify(title) must:
1. Lowercase the title.
2. Replace runs of whitespace with a single hyphen.
3. Remove characters that are not letters, digits, or hyphens.
   slugify("Hello, World!") must return "hello-world".
