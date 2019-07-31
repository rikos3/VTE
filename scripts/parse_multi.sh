#!/bin/bash

# Usage: parse the sentence in input.txt
# ./parse_sv.sh <parser>
#
# <parser> ::= candc | easyccg | depccg

parser=$1

home=$HOME
c2l_dir="${home}/ccg2lambda"
mm_dir="${home}/multimodal_inference"
candc_dir="${home}/candc-1.00"
easyccg_dir="${home}/easyccg"
depccg_dir="${home}/depccg"
depccg_sv_dir="${home}/.opam/system"
templates="${mm_dir}/semantics/semantic_templates_en_image.yaml"

input="${mm_dir}/input.txt"

# Set up soap_server
# at $candc_dir:
# ./bin/soap_server --models models --server localhost:8800 --candc-printer xml

# depccg
# at $depccg_sv_dir:
# python lib/depccg/server.py share/depccg/tri_headfirst
# unlink /tmp/tagging_server

# Tokenize input sentence
cat $input | \
  sed -f $c2l_dir/en/tokenizer.sed | \
  sed 's/ _ /_/g' | \
  sed 's/[[:space:]]*$//' |
  sed -e 's/$/\n/g' \
  > $input.tok

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
    --input $input.tok \
    > $input.candc.xml \
    2>/dev/null \
  # Convert plain xml to jigg xml
  python -E $c2l_dir/en/candc2transccg.py $input.candc.xml \
    > $input.candc.jigg.xml \
    2> /dev/null
  rm $input.candc.xml 
# EasyCCG parsing
elif [ ${parser} == "easyccg" ]; then
  pos_tagging $input.tok | \
  java -jar ${easyccg_dir}/easyccg.jar \
    --model ${easyccg_dir}/model \
    -i POSandNERtagged \
    -o extended \
    --maxLength 100 \
    > $input.easyccg \
    2>/dev/null
  python -E ${c2l_dir}/en/easyccg2jigg.py \
      $input.easyccg \
      $input.easyccg.jigg.xml \
      2>/dev/null
  rm $input.easyccg
# depccg parsing
elif [ ${parser} == "depccg" ]; then
  cat $input.tok | \
  env CANDC=${candc_dir} depccg_en \
    --input-format raw \
    --annotator candc \
    --format jigg_xml \
  > ${parsed_dir}/$input.depccg.jigg.xml \
  2> ${parsed_dir}/$input.log
else
  echo "no such parser exists!"
fi

# Semantic parging: convert jigg xml to formula
python -E $c2l_dir/scripts/semparse.py \
  $input.$parser.jigg.xml \
  $templates \
  $input.$parser.sem.xml \
  2> /dev/null

# Convert formula to normalized form (remove True etc.)
python -E $c2l_dir/scripts/convert_formulas.py \
  $input.$parser.sem.xml --format fol

# rm $input.tok $input.$parser.jigg.xml $input.$parser.sem.xml
