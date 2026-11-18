% APPROXIMATE stand-in for iitdamthes.cls, ONLY for local page counting
\NeedsTeXFormat{LaTeX2e}\ProvidesClass{iitdamthes}
\LoadClass[12pt,a4paper]{report}
\RequirePackage{setspace}\setstretch{1.5}
\setlength{\textwidth}{450pt}\setlength{\textheight}{635pt}
\setlength{\oddsidemargin}{0pt}\setlength{\topmargin}{-20pt}\setlength{\headsep}{40pt}
\newcommand{\supervisor}[1]{}\newcommand{\submitdate}[1]{}\def\btech{}\def\endsem{}\def\midsem{}
\newif\iftablespage\newif\iffigurespage
\newcommand{\studentdeclaration}{\chapter*{Declaration}x\clearpage}
\newcommand{\supervisorcertificate}{\chapter*{Supervisor Certificate}x\clearpage}
\newcommand{\prefacesection}[1]{\chapter*{#1}}
\newcommand{\acknowledgements}{\prefacesection{Acknowledgements}}
\newcommand{\notations}{\prefacesection{Notation and Abbreviations}}
\renewenvironment{abstract}{\prefacesection{Abstract}}{}
\newenvironment{frontmatter}{\pagenumbering{roman}}{\clearpage\pagenumbering{arabic}}
\newcommand{\makecontents}{\tableofcontents\listoffigures\listoftables}
\def\ps@bfheadings{\ps@headings}
