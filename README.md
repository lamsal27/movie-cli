# movie-cli

Browse and stream movies from your terminal.

## Requirements

- Python 3.10+
- [fzf](https://github.com/junegunn/fzf#installation)
- A free [TMDB token](https://www.themoviedb.org/settings/api)

## Install

```bash
git clone https://github.com/lamsal27/movie-cli
cd movie-cli
pip install httpx python-dotenv
```

Install fzf:

```bash
brew install fzf        # macOS
sudo apt install fzf    # Ubuntu/Debian
scoop install fzf       # Windows
```

## Run

```bash
python movies.py
```

First run will prompt for your TMDB token. Saved to `.env` — never asked again.

## Controls

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate |
| Type | Fuzzy filter |
| `Enter` | Select |
| `Esc` | Go back |

## License

[GPL-3.0](LICENSE)
