# Movie-CLI - Watch movies from terminal

**movie-cli** is a terminal-based application built with Node.js that allows users to search for movies, extract streaming links via web scraping, and play them directly using `mpv` or `vlc` —all without requiring any external APIs.

> ✨ Heavily inspired by [ani-cli](https://github.com/pystardust/ani-cli)

---

## Key Features

- Efficient movie search using IMDb (via unofficial endpoints)
- Presents top 5 matching results with title, release year, and IMDb ID
- Leverages Puppeteer to extract, streaming URLs from public piracy sites
- Plays selected movie stream using `mpv` player

---

## ⚙️ Prerequisites

To use movie-cli, you need the following:

- [Node.js](https://nodejs.org/) version 18 or higher
- [`mpv`](https://mpv.io/) media player installed globally on your system
- [Google Chrome](https://www.google.com/chrome/) or Chromium browser for Puppeteer automation
- A stable internet connection

> Note: Currently optimized for Unix-based systems (Linux/macOS); Windows support is untested.

---

## 📦 Installation

Clone the repository and install the dependencies:

```bash
git clone http://github.com/lamsal27/movie-cli.git
cd movie-cli
npm install
```

---

## How to Use

Run the script using Node.js:

```bash
node movie_cli.js
```

Follow the on-screen prompts:

1. Enter the name of the movie you're looking for
2. Select a result from the displayed list
3. The program fetches the stream link and plays it in `mpv`

---

## Contribution Guidelines

Contributions are encouraged and appreciated!

Ways to contribute:

- 📊 Report issues or bugs
- 🚀 Suggest new features
- 📚 Submit pull requests

To contribute:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes and commit them
4. Push to your fork
5. Submit a pull request

Please maintain clean coding standards and ensure your changes are functional before submission.

---

## License

This project is distributed under the **GNU General Public License v3.0**.

Read the full license [here](https://www.gnu.org/licenses/gpl-3.0.html).

---

 Legal Disclaimer

This tool is intended strictly for educational and personal experimentation. It does not host, promote, or redistribute any copyrighted material. All video sources are retrieved through publicly accessible web content. The author neither encourages nor condones the use of this tool to violate any terms of service or local copyright laws.
Use at your own discretion. The responsibility for how this script is used lies entirely with the end user.

---

## 🚀 Acknowledgements

- Inspired by [ani-cli](https://github.com/pystardust/ani-cli) — a terminal tool for anime streaming
- Designed for users who prefer lightweight, CLI-based media solutions
