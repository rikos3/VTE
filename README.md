## Multimodal Logical Inference System for Visual-Textual Entailment
Codebase for [Multimodal Logical Inference System for Visual-Textual Entailment](https://arxiv.org/abs/1906.03952)

### Requirements
- Python >= 3.6.0
- [Vampire](https://github.com/vprover/vampire) >= 4.3.0
- [Prover9](https://www.cs.unm.edu/~mccune/prover9/)
- [ccg2lambda](https://github.com/mynlp/ccg2lambda)

### Installation
Install ccg2llambda & CCG parser
```
git clone https://github.com/mynlp/ccg2lambda.git
pip install lxml simplejson pyyaml nltk
```

Install Prover9
```
wget http://www.cs.unm.edu/~mccune/mace4/download/LADR-2009-11A.tar.gz
tar xvzf LADR-2009-11A.tar.gz 
mv LADR-2009-11A prover9
cd prover9/
make all
make test1
make test2
make test3
```

Clone our repository
```
git clone https://github.com/rikos3/VTE.git
```

Download VisualGenome (2GB)
```
wget http://imagenet.stanford.edu/internal/jcjohns/scene_graphs/sg_dataset.zip
unzip sg_dataset.zip
mv sg_dataset VTE/.
```

### Usage

### Citation
```
@inproceedings{suzuki-etal-2019-multimodal,
    title = "Multimodal Logical Inference System for Visual-Textual Entailment",
    author = "Suzuki, Riko and Yanaka, Hitomi and Yoshikawa, Masashi and Mineshima, Koji and Bekki, Daisuke",
    booktitle = "Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop",
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/P19-2054",
    doi = "10.18653/v1/P19-2054",
    pages = "386--392",
}
```