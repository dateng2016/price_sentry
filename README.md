# Price Sentry

Price Sentry is a FastAPI-based application that allows users to search for products on vendors like Amazon, track price changes, and receive notifications when their desired products' prices fluctuate.

**Note:** Currently, Price Sentry only supports Amazon as a vendor. Support for additional vendors is being developed. Additionally, the frontend for this project is still in development.

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Usage](#usage)
-   [API Endpoints](#api-endpoints)
-   [License](#license)
-   [Contact](#contact)

## Features

-   Search for products across multiple vendors like Amazon.
-   Track prices for selected products.
-   Receive notifications when prices change.
-   User-friendly interface with FastAPI.

## Installation

Before you install the necessary python packages, make sure you have the following installed on your computer: libmysqlclient-dev, pkg-config, libssl-dev.

In Ubuntu you can install them with:

```bash
sudo apt install libmysqlclient-dev
sudo apt install pkg-config
sudo apt install libssl-dev
```

Then, run the following command to set the flags for mysql client:

```bash
export MYSQLCLIENT_CFLAGS="$(mysql_config --cflags)"
export MYSQLCLIENT_LDFLAGS="$(mysql_config --libs)"
```

Now clone the repository and install the python packages with the following commands.

```bash
git clone https://github.com/dateng2016/price_sentry.git
cd price-sentry
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

Before starting the service, create a `.env` file in the root directory of the project. Add the necessary variables inside the file. Here is an example of the content for the `.env` file. In this project, I used gmail to send out emails. If you intend to do the same you need to set up your app password in your gmail account.

```dotenv
# Database
DB_HOST=localhost:3306
DB_USER=root
DB_PASSWD=""
DB_NAME=price_sentry
# Secret
SECRET=test123
# Email
EMAIL_FROM=youremail@xxx.com
APP_PASSWORD=yourapppassword
```

Then, go into your mysql database and create a database named price_sentry (or any other name is your DB_NAME is set to be a different name in your `.env` file)

**Note:** if your plugin for the desired DB_USER is auth_socket, you might need to change it to caching_sha2_password. Otherwise, you might experience authentication issues when running with aiomysql.

Also, add a `/log` directory and a `/scraper/amazon/page_source` directories because github did not let me upload empty directories ;)

Now, you are ready to start the service! Simply go into the root directory of the project and run the following command to start the FastAPI service:

```bash
uvicorn app:app --reload
```

Once you get the service started, also remember to run the `price_monitor.py` in the background so that it can track the price of the products in the database and notify the corresponding users when the prices fluctuate.

```bash
python price_monitor.py
```

## Usage

For testing, a test.ipynb file is included in the root directory.

## API Endpoints

For detailed information on the API endpoints, visit the documentation at http://127.0.0.1:8000/docs once the service is up and running.

## License

This project is licensed under the MIT License.

### License Summary

MIT License: You are free to use, modify, and distribute the software, provided that all copies include the original copyright and license notice. This license also provides a disclaimer of warranties, meaning that the software is provided "as is" without any guarantees or warranties.

## Contact

For any questions or inquiries, please contact:

Project Maintainer: Da Teng
Support Email: dateng2016@gmail.com
Project Repository: https://github.com/dateng2016/price_sentry
Feel free to open an issue or submit a pull request on the GitHub repository if you have suggestions or improvements.
