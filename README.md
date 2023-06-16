# MLE2SP

#### 1. Download Raw data `sslp_data`,`sstp_data`,`size_data`.
 download link:

`sslp_data`: https://www2.isye.gatech.edu/~sahmed/siplib/sslp/sslp.html

`sstp_data`: http://users.iems.northwestern.edu/~jrbirge/html/dholmes/post.html

`size_data`: https://www2.isye.gatech.edu/~sahmed/siplib/sizes/sizes.html

#### 2. Use `bench2data` read data in `sslp_data`,`sstp_data`,`size_data` into dictionary and save in `bench2SP_data`.

extra : Read raw data and convert it to standard `mps` `lp` format with gurobi[<sup>1</sup>](#refer-anchor-1) and save it in `bench2SP_mps - 副本`.

<div id="refer-anchor-1"></div>

- [1] [gurobi](https://www.gurobi.com/)

#### 3. Realize the objective function SSTP,SSLP,SIZE in `bench2fitness_sslp_sstp_size.py` based on the input instance data.

#### 4. Evaluation using GA, MI-EDDE, MLDES in `MLDES,GA,MI-EDDE,DRLP CODE.zip`.

Evaluation functions include sslp, sstp, size, drlp.

> The decompression password of the MLDES,GA,MI-EDDE,DRLP CODE.zip file is the paper ID "TETCI-****".
> After the paper is published, it is completely open source, and the decompression password is released.
