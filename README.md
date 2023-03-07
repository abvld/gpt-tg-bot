<h1 align="center">💬 <b>gpt-tg-bot</b> - personal ChatGPT Telegram bot (Telegram API and OpenAI API)</h1>

<p align="center">
  <img src="https://images2.imgbox.com/b1/c2/wcdAynMe_o.png" width="800"/>
</p>

Run your personal ChatGPT bot for Telegram using the OpenAI API. The bot is using "gpt-3.5-turbo" model.


## ✅ **Features**

**Token usage count**

<p align="center">
  <img src="https://images2.imgbox.com/f3/03/E5PLOHuL_o.png" width=800/>
</p>

The bot extracts token usage statistics from the model's responses, and calculates the total value of the current chat based on the price on the site ($0.002/1K tokens).

**Copyable code blocks**

<p align="center">
  <img src="https://images2.imgbox.com/bb/4f/iwTcUs7o_o.png" width=800/>
</p>

One-click code copypaste from code blocks.


**Persistent storage**

The bot uses the local pickle data file storage to save messages in currently active chats.

**Preserved context**

The model has access to previous messages in the currently active chat, preserving the context.


## ⚙️ **Installation guide**

1. Export your OpenAI and Telegram API keys.

```bash
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
export TELEGRAM_API_TOKEN=YOUR_TELEGRAM_API_KEY
```

2. Install the requirements

```bash
pip install -r requirements.txt
```

3. Launch the bot

```bash
python -m gpt_tg_bot
```


## 📄 **Disclaimer**

This project is using APIs from OpenAI and Telegram. The developers of this project are not responsible for any damages, losses, or legal issues that may arise from the use of this software.

This project is not affiliated with or endorsed by OpenAI or Telegram in any way. The developers of this project do not claim ownership of any intellectual property associated with OpenAI or Telegram. The APIs used in this project are subject to the terms and conditions set forth by OpenAI and Telegram, respectively.

Users of this project are solely responsible for complying with the terms and conditions set forth by OpenAI and Telegram. The developers of this project do not assume any liability for any violations of these terms and conditions.