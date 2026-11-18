# End-semester report (LaTeX)

Files: `report.tex`, `references.bib`, `figures/*.png`.

**To compile for submission:** upload this folder to Overleaf (or your LaTeX setup) together with the
department's real `iitdamthes.cls` and `iitdlogo` files from the template, then run pdfLaTeX → BibTeX →
pdfLaTeX → pdfLaTeX.

`report_PREVIEW_stub_class.pdf` was compiled with an approximate stand-in class
(`../tools/iitdamthes_stub/iitdamthes.cls`: same 12 pt font, 1.5 spacing, 450 × 635 pt text block),
**only to check the page count** (main body = 10 pages). The title page, declaration and certificate
pages are placeholders in this preview. Check the page count again after compiling with the real class.

Before submitting:
- fill in the **Contribution of Authors** section (marked TODO in `report.tex`);
- check the **AI-use disclosure** in the Acknowledgements;
- check the submission date (`\submitdate`).
