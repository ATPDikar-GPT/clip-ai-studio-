# Security notes

- Never commit OpenAI API keys, Twitch OAuth tokens, passwords, `.env` files or local Streamlit secrets.
- Treat screenshots of settings and terminal output as potentially sensitive.
- If a credential is exposed, revoke/rotate it with the provider; deleting the file or commit is not sufficient.
- Keep user videos, chat logs, project data and exported clips outside public Git repositories.
- Use Twitch and third-party video services only in accordance with their terms and with permission to process the content.
