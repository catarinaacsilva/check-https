# Check HTTPS on Websites



## Run

1. Create a venv:

    `python3 -m venv venv`

2. `source/venv/bin/activate`

3. Install requirements:

    `pip install -r requirements`

4. Run tests


# Selenium

## Install ubuntu 18.04

1. Install Selenium

    'pip install selenium`

2. Selenium requires a driver to interface with the chosen browser

    Firefox:

        `wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz`

        `tar xvzf geckodriver-v0.24.0-linux64.tar.gz`

        `chmod +x geckodriver`

        `export PATH=$PATH:/path-to-extracted-file/.`

        `sudo mv geckodriver /usr/local/bin/`


## Authors

* **Catarina Silva** - [catarinaacsilva](https://github.com/catarinaacsilva)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details