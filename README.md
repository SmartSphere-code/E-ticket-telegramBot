# E-TicketBot

E-TicketBot streamlines the process of buying and selling digital tickets with unparalleled ease. Enjoy instant delivery, secure transactions, and user-friendly features, all within Telegram.

## Technologies

- **Python** - Codebase
- **Paystack** - Universal Payment Gateway
- **PostgreSQL 16** - Ticket and transaction reference database

## Installation

Start by cloning the repository:

```bash
git clone https://github.com/SmartSphere-code/E-ticket-telegramBot.git

cd E-ticket-telegramBot

pip -r install requirements.txt
```
### Configurations (`config.py`)

To configure E-TicketBot, you need to set up both the Paystack payment gateway and the database. This guide assumes you are using a hosted PostgreSQL 16 database.

- **`TOKEN`**: Update with token received from @botfather
#### Paystack Setup

- **`SECRET_KEY`**: Update with your Paystack secret key.
- **`CALLBACK_URL`**: Update with the URL of the server hosting this project or an ngrok port-forwarded URL. Ensure it ends with `/genv`.

**Ticket Pricing:**

Ticket prices can be adjusted based on your needs and more options can be added,below are the preconfigured ones.
- **`STANDARD`**: 50
- **`DOUBLE`**: 80
- **`VIP`**: 120

#### Database Setup

**Database for handling Telegram users:**
- **`DB_USERNAME`**: Replace with the username provided by your database provider.
- **`DB_PASSWORD`**: Replace with your database password.
- **`DB_HOST`**: Replace with the database host address.
- **`DB_DATABASE`**: Replace with your database name.

**Database for handling ticket numbers, types, and validity:**
- **`PGHOST`**: Replace with the database host address.
- **`PGDATABASE`**: Replace with your ticket database name.
- **`PGUSER`**: Replace with the username provided by your database provider.
- **`PGPASSWORD`**: Replace with your database password.

- **`VERIFY_ENDPOINT`**: Update with the URL of the server hosting this project or an ngrok port-forwarded URL (if applicable).

## Contribution

E-TicketBot is an open-source project, and we welcome contributions from the community.

If you'd like to contribute, please fork the repository and make your changes. 

Pull requests are warmly welcomed.
