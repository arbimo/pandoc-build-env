import re

# http://www.pythonregex.com/

png_re = re.compile("!\[(?P<caption>[^\]]*)\]\((?P<path>[^\)]+\.png)\)$")
csv_re = re.compile("!\[(?P<caption>[^\]]*)\]\((?P<path>[^\)]+\.csv)\)$")

tex_figure = ("\\begin{figure}[H]\n"
              "  \centering\n"
              "  \includegraphics[width=\mymaxwidth]{---path---}\n"
              "  \caption{---caption---}\n"
              "\\end{figure}\n")
              
tex_table =  ("\\begin{table}\n"
              "  \\csvautotabular{---path---}\n"
              "  \\caption{---caption---}\n"
              "\\end{table}\n")


ins = open( "rapport.md", "r" )

for line in ins:
  png = png_re.search(line)
  csv = csv_re.search(line)
  if(png):
    caption = png.groupdict()[ "caption" ]
    path = png.groupdict()[ "path" ]
    print tex_figure.replace("---caption---", caption).replace("---path---", path)
  elif(csv):
    caption = csv.groupdict()[ "caption" ]
    path = csv.groupdict()[ "path" ]
    print tex_table.replace("---caption---", caption).replace("---path---", path)
  else:
    print line.rstrip('\n')



