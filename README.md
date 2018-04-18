# Librio

Librio is a python script that rebalances your Binance Exchange Portfolio according to the percentage allocations in `data.json`

## Getting Started


* You will need python installed.
* You need to have a Binance account with some $$$ in crypto.
* You will also need to have an api key enabled. Please be **very careful** with this key.
* **Don't upload it to anything and if possible set the api setting to limit IP addresses.**

### Installing

Copy your API KEY and SECRET to the appropriate places in `config.py`

```
git clone https://github.com/Daniel-Wang/librio.git
cd librio
```


## Running the script

Take some time to adjust the numbers and the symbols of your preferred portfolio composition in `data.json`.

Set `OFFLINE` to `false` in `config.py`

```
python main.py
```


## Contributing

If you want to help improve Librio please submit a Pull Request.
Some possible suggestions on things to submit:

* Improve rebalancing algorithm (current one is brute force simple)
* Add support for more exchanges
* Improve the user experience


## Authors

**Daniel Wang**

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License.

## Acknowledgments

* https://medium.com/@ShrimpyApp/portfolio-rebalancing-for-cryptocurrency-7a129a968ff4
* Inspiration
* Please give this project a star if you found it helpful or useful!

