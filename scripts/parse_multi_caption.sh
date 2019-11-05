#!/bin/bash

# Usage: parse the sentence. 
# ./parse_multi_caption.sh <parser> <file_key>
#
# <parser> ::= candc | easyccg | depccg
# <file_key> ::= file key in GRIM dataset

parser=$1

home=$HOME
c2l_dir=`cat ccg2lambda_location.txt`
vte_dir=`cat vte_location.txt`
candc_dir="${c2l_dir}/en/candc-1.00"
easyccg_dir="${c2l_dir}/en/easyccg"
#depccg_dir="${home}/depccg"
#depccg_sv_dir="${home}/.opam/system"
templates="${vte_dir}/semantics/semantic_templates_en_image.yaml"

if [ ! -d "${vte_dir}/input" ]; then
  mkdir ${vte_dir}/input
fi

input="${vte_dir}/input/input.txt"

key=$2
input="${vte_dir}/grim/data/${key}.t"
output="${vte_dir}/work/captions/${key}"

# Set up soap_server
# at $candc_dir:
# ./bin/soap_server --models models --server localhost:8800 --candc-printer xml

# depccg
# at $depccg_sv_dir:
# python lib/depccg/server.py share/depccg/tri_headfirst
# unlink /tmp/tagging_server

# Tokenize input sentence
cat $input | \
  sed -e 's/\r//g' | \
  sed -f $c2l_dir/en/tokenizer.sed | \
  sed 's/ _ /_/g' | \
  sed 's/[[:space:]]*$//' |
  sed -e 's/$/\n/g' \
  > $output.tok

python word2num_shell.py $output.tok $output.tok.w2n

function lemmatize() {
    # apply easyccg's lemmatizer to input file
    fname=$1
    lemmatized=`mktemp -t tmp-XXX`
    cat $fname | java -cp ${easyccg_dir}/easyccg.jar \
        uk.ac.ed.easyccg.lemmatizer.MorphaStemmer \
        > $lemmatized \
        2>/dev/null
    paste -d "|" $fname $lemmatized | \
        awk '{split($0, res, "|");
             slen = split(res[1], sent1);split(res[2], sent2);
             for (i=1; i <= slen; i++) {
                printf sent1[i] "|" sent2[i]
                if (i < slen) printf " "
            }; print ""}'
}

function pos_tagging() {
  fname=$1
  cat $fname | \
  ${candc_dir}/bin/pos \
    --model ${candc_dir}/models/pos \
    2>/dev/null | \
  ${candc_dir}/bin/ner \
    -model ${candc_dir}/models/ner \
    -ofmt "%w|%p|%n \n" \
    2>/dev/null
}


# C&C parsing
if [ ${parser} == "candc" ]; then
  # When soap server mode is available:
  # cat $input.tok | \
  #   $candc_dir/bin/soap_client --url http://localhost:8800 \
  #   2>/dev/null \
  #   > $input.candc.xml
  ${candc_dir}/bin/candc \
    --models ${candc_dir}/models \
    --candc-printer xml \
    --input $output.tok.w2n \
    > $output.candc.xml \
    2>/dev/null \
  # Convert plain xml to jigg xml
  python -E $c2l_dir/en/candc2transccg.py $output.candc.xml \
    > $output.candc.jigg.xml \
    2> /dev/null
#  rm $output.candc.xml 
# EasyCCG parsing
elif [ ${parser} == "easyccg" ]; then
  pos_tagging $output.tok.w2n | \
  java -jar ${easyccg_dir}/easyccg.jar \
    --model ${easyccg_dir}/model \
    -i POSandNERtagged \
    -o extended \
    --maxLength 100 \
    > $output.easyccg \
    2>/dev/null
  python -E ${c2l_dir}/en/easyccg2jigg.py \
      $output.easyccg \
      $output.easyccg.jigg.xml \
      2>/dev/null
  rm $output.easyccg
# depccg parsing
elif [ ${parser} == "depccg" ]; then
  lemmatize $output.tok.w2n | \
  ${candc_dir}/bin/pos \
      --model ${candc_dir}/models/pos \
      --ifmt "%w|%l \n" \
      --ofmt "%w|%l|%p \n" \
      2>/dev/null | \
  ${candc_dir}/bin/ner \
      --model ${candc_dir}/models/ner \
      --ifmt "%w|%l|%p \n" \
      --ofmt "%w|%l|%p|%n \n" \
      2> /dev/null | \
  python -E ${depccg_dir}/src/run.py \
      ${depccg_dir}/models/tri_headfirst \
      en \
      --input-format POSandNERtagged \
      --format xml \
      2>/dev/null \
      > $output.depccg.xml
  python $c2l_dir/en/candc2transccg.py $output.depccg.xml \
    > $output.depccg.jigg.xml \
    2>/dev/null
  rm $output.depccg.xml
else
  echo "no such parser exists!"
fi

# Semantic parging: convert jigg xml to formula
python -E $c2l_dir/scripts/semparse.py \
  $output.$parser.jigg.xml \
  $templates \
  $output.$parser.sem.xml \
  2> /dev/null

# Convert formula to normalized form (remove True etc.)
python -E $c2l_dir/scripts/convert_formulas.py \
  $output.$parser.sem.xml --format fol

# rm $output.tok $output.$parser.jigg.xml $output.$parser.sem.xml
