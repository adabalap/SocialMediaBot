# SocialMediaBot
Social media bot fetches quotes from Gemini AI service &amp; posts them (Twitter, WordPress, WhatsApp) with error handling. Runs in loop, checks for unique quotes &amp; stores details in database. Functionality depends on configuration &amp; external services.

A configurable social media bot designed to automatically post quotes on various platforms.

**Setting Up:**
The bot loads instructions (configuration file) and prepares to record its actions (logging) and store quotes in a database.

**Fetching Quotes:**
The bot retrieves quotes from an external service (likely a GenAI model) via a web request.
It processes the response to extract the quote and speaker's name, formatting the quote slightly.

**Posting Capabilities:**
The bot can post on Twitter, WordPress, and WhatsApp.
Twitter posts include a customizable prefix and suffix added to the quote.
For WordPress, it can create new posts or update existing ones with the quote.
WhatsApp functionality involves sending the quote as a message to a designated chat.

**Running the Bot:**
The bot operates within a loop, attempting to post quotes a set number of times.
In each loop, it generates a new quote, checks for uniqueness in the database, and if unique, posts it to the configured platforms.
Details about each posted quote are stored in the database.

**Error Handling:**
The bot manages errors, logging issues like exceeding Twitter's character limit or problems with WordPress/WhatsApp.

**Note:**
The specific functionalities depend on the configuration provided.
External services like the quote provider and social media platforms can influence the bot's behavior.
