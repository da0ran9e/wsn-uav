"""body_raw.tex (pandoc) -> body.tex: sections renumbered by LaTeX, figure captions, math, ND1 block."""
import re
s = open("body_raw.tex").read()
# drop title section and draft notes before section 1
s = s[s.index("\\subsection{1. Tóm tắt}"):]
# headings: \subsection{N. X} -> \section{X}; \subsubsection{N.M X} -> \subsection{X}; drop pandoc labels
s = re.sub(r"\\subsection\{(?:\\texorpdfstring\{)?\d+\.\s*", r"\\section{", s)
s = re.sub(r"\\subsubsection\{\d+\.\d+\s*", r"\\subsection{", s)
s = s.replace("\\subsection{Phụ lục}", "\\section*{Phụ lục}")
# figures: caption from the following \emph{Hình N. ...} paragraph
def fig(m):
    path, cap = m.group(1), m.group(3)
    path = path.replace("../../", "../../../", 1)
    return ("\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=0.82\\linewidth,height=0.38\\textheight,keepaspectratio]{%s}\n"
            "\\caption{%s}\n\\end{figure}\n" % (path, cap.strip()))
s = re.sub(r"\\begin\{figure\}\s*\\centering\s*\\includegraphics\{([^}]*)\}\s*\\caption\{(.*?)\}\s*\\end\{figure\}\s*"
           r"\\emph\{Hình \d+\.\s*(.*?)\}\n", fig, s, flags=re.S)
s = re.sub(r"\\includegraphics\{([^}]*)\}\s*\\emph\{Hình \d+\.\s*(.*?)\}\n",
           lambda m: fig(type("M", (), {"group": lambda self, i: {1: m.group(1), 3: m.group(2)}[i]})()), s, flags=re.S)
# ND1 model + results block -> hand-written LaTeX
a = s.index("\\textbf{Mô hình chung.}"); b = s.index("\\textbf{Kiểm chứng.}")
block = s[a:b]
m9 = re.search(r"\\begin\{figure\}.*?prop-b-deviation-threshold.*?\\end\{figure\}\n", block, flags=re.S)
s = s[:a] + open("nd1.tex").read().replace("%FIG9%", m9.group(0)) + s[b:]
# symbols
s = s.replace("T*", "$T^\\star$").replace("R50", "$R_{50}$")
open("body.tex", "w").write(s)
print("figures:", s.count("\\begin{figure}"), "sections:", s.count("\\section{"))
