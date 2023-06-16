# MLE2SP

#### 1. Download Raw data `sslp_data`,`sstp_data`,`size_data`.
 download link:

`sslp_data`: https://www2.isye.gatech.edu/~sahmed/siplib/sslp/sslp.html

`sstp_data`: http://users.iems.northwestern.edu/~jrbirge/html/dholmes/post.html

`size_data`: https://www2.isye.gatech.edu/~sahmed/siplib/sizes/sizes.html

#### 2. Use `rSIZE` `rSSLP` `rSSTP` read data in `sslp_data`,`sstp_data`,`size_data` into dictionary and save in `bench2SP_data`.

extra : Read raw data and convert it to standard `mps` `lp` format with gurobi[<sup>1</sup>](#refer-anchor-1) and save it in `bench2SP_mps - 副本`.

<div id="refer-anchor-1"></div>

- [1] [gurobi](https://www.gurobi.com/)
