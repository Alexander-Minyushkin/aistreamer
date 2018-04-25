cat data/reddit/Games_10.txt data/reddit/WritingPrompts_10.txt data/pg/Best_books.txt data/pg/Sheckley_Robert.txt| 
iconv -c -f utf-8 -t ascii | iconv -f ascii -t utf-8 | 
tr '[:upper:]' '[:lower:]' | 
tr -d '[]()' | 
sed '/^\s*$/d' | sed 's/\_/ /g' |
sed "s/[\r\t;]/ /g" | sed 's/[,+]/ /g' | sed '/http/d' | 
tr -d '\n' |
sed 's/\./\n /g' | sed 's/!/ !\n /g' |  sed 's/?/ ?\n /g' |  
sed '/\^/d' | sed 's/"//g' | 
sed 's/&gt//g' | sed 's/\*/ /g' | sed '/[#\/]/d' | tr -s ' ' | sed 's/^ //g' |
sed '/./!d' | sed '/.\{150\}/d' | sed '/^\s*$/d' > tmp/combined.txt




 head -n150 data/pg/Sheckley_Robert.txt | 
 iconv -c -f utf-8 -t ascii | iconv -f ascii -t utf-8 |  tr '[:upper:]' '[:lower:]' |  
 tr -d '[]()' | tr '\r\n_' '   ' | 
 sed 's/\./ .\n/g' | sed 's/!/ !\n/g' | sed 's/?/ ?\n/g' |
 sed 's/[,;\"-]/ /g' | 
 tr -s ' ' | 
 sed 's/\* \* \* \* \* /\n/g' | 
 sed 's/^ //g'

