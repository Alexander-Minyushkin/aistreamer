cat data/reddit/Games_10.txt data/reddit/WritingPrompts_10.txt | 
iconv -c -f utf-8 -t ascii | tr '[:upper:]' '[:lower:]' | 
tr -d '[]()' | sed "s/[\r\t;]/ /g" | sed 's/[,+]/ /g' | 
sed 's/\./\n /g' | sed '/\^/d' | sed '/http/d' | sed 's/"//g' | 
sed 's/&gt//g' | sed 's/\*/ /g' | sed '/[#\/]/d' | tr -s ' ' | 
sed '/./!d' > tmp/combined.txt
