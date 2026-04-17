# AliExpress Telegram Bot

## Features
- Search for products on AliExpress directly from Telegram.
- Get product details including price, shipping options, and seller ratings.
- Save favorite products to view later.
- Receive notifications for price drops and special promotions.
- Multilingual support for users.

## Installation
1. **Clone the repository**:  
   ```bash
   git clone https://github.com/mesbaheidire/AliExpress-Bot1.git
   ```
2. **Navigate to the project directory**:  
   ```bash
   cd AliExpress-Bot1
   ```
3. **Install dependencies**:  
   ```bash
   npm install
   ```

## Deployment on Render
1. **Create a Render account** if you don't have one.
2. **Create a new Web Service:**  
   - Choose the GitHub repository you cloned.
   - Set the environment to Node.
   - Configure the build command to `npm install` and the start command to `npm start`.
3. **Set environment variables**:  
   - `TELEGRAM_API_KEY`: Your Telegram bot API key.
   - `ALIEXPRESS_API_KEY`: Your AliExpress API key.
4. **Deploy your service.**

## Usage Instructions
- Start a conversation with the bot on Telegram by searching for its username.
- Use the `/start` command to initiate.
- Search for products using the command `/search <product-name>`. 
- For favorite products, use `/favorite` command to view your saved items.
- Prices can be monitored for products you are interested in. 

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, please reach out to [your-email@example.com].