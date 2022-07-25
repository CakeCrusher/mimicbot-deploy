# mimicbot-deploy 🤖
## About
Mimicbot-deploy is an accompanying repository to the [mimicbot](https://github.com/CakeCrusher/mimicbot) cli. It is intended to be used for exclusively deploying the discord bot to a server.
## Deploy
To deploy the bot to a server follow the steps below:
1. Clone the repository `git clone https://github.com/CakeCrusher/mimicbot-deploy.git`.
2. Install the dependencies `pip install -r requirements.txt`.
3. In your [mimicbot cli](https://github.com/CakeCrusher/mimicbot) directory run the command `python -m mimicbot poduction_env`.
4. Navigate to the data path you configured in init (if you don't remember it you can run `python -m mimicbot config`, then locate `data_path`). Copy the files inside the `deploy` directory into this (mimicbot-deploy) directory.
5. Verify that the discord bot is running as intended. Run `python mimic.py` and message your mimicbot with `@<YOUR_BOT_NAME> <ANY_TEXT_YOU_WANT_IT_TO_REPLY_TO>`.
### Heroku
6. Create a heroku app.
7. [Add the environment variables](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard) listed in the `.env` file to your heroku app.
8. Follow the directions in the deploy tab of your heroku app.
9. You have now deployed your bot to a server.