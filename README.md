# Check HTTPS on Websites

The main goal of this project is to check the HTTPS on websites. It can be applied on all the websites. Currently, the project has an old interface to insert the name of the website and test. Thus, at this moment is possible using python scripts test any website.

The project was developed using python3 and Flask.

Future work ( I do not know when :) ):

- Convert to django
- Design and implement an interface to interact with the system.

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

2. Selenium requires a driver to interface with the chosen browser (Firefox)
    2.1 `wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz`
    2.2 `tar xvzf geckodriver-v0.24.0-linux64.tar.gz`
    2.3 `chmod +x geckodriver`
    2.4 `export PATH=$PATH:/path-to-extracted-file/.`
    2.5 `sudo mv geckodriver /usr/local/bin/`


## Authors

* **Catarina Silva** - [catarinaacsilva](https://github.com/catarinaacsilva)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details