#!/usr/bin/env python3

import os, shutil, subprocess, sys, textwrap
from pathlib import Path
from dotenv import load_dotenv, set_key
import httpx

API = "https://api.themoviedb.org/3"
ENV = Path(".env")

THEME = (
    "--color=fg:#f8c8d4,fg+:#ffffff,bg:-1,bg+:#3d1a26,"
    "hl:#ff79c6,hl+:#ff79c6,"
    "prompt:#ff79c6,pointer:#ff79c6,marker:#ff79c6,"
    "border:#bf5f82,label:#ff79c6,header:#f8c8d4,"
    "info:#f8c8d4,spinner:#ff79c6"
)

def require_fzf():
    if shutil.which("fzf"):
        return
    print("fzf is required.  https://github.com/junegunn/fzf#installation")
    print("  macOS:  brew install fzf")
    print("  Ubuntu: sudo apt install fzf")
    print("  Windows: scoop install fzf")
    sys.exit(1)

def get_token() -> str:
    load_dotenv(ENV)
    if t := os.getenv("TMDB_TOKEN", "").strip():
        return t
    clear()
    print("── TMDB Token Required ───────────────────────────────")
    print("  https://www.themoviedb.org/settings/api")
    print("  Sign up → Settings → API → API Read Access Token")
    print("─────────────────────────────────────────────────────\n")
    t = input("Paste token: ").strip()
    if not t:
        sys.exit("No token provided.")
    ENV.touch()
    set_key(str(ENV), "TMDB_TOKEN", t)
    print("\n✓ Saved to .env — won't be asked again.")
    input("Press enter to continue...")
    return t

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def fzf(items: list[str], prompt: str = "") -> str | None:
    args = [
        "fzf", "--ansi", "--cycle",
        f"--prompt= {prompt}  ",
        "--pointer=›",
        "--height=~80%",
        "--layout=reverse",
        "--border=rounded",
        "--border-label=  movie-cli  ",
        "--border-label-pos=3",
        THEME,
    ]
    r = subprocess.run(args, input="\n".join(items), capture_output=True, text=True)
    return r.stdout.strip() or None

def get(client: httpx.Client, path: str, **params) -> dict:
    r = client.get(f"{API}{path}", params=params)
    if r.status_code == 401:
        sys.exit("✗ Invalid token. Delete .env and retry.")
    r.raise_for_status()
    return r.json()

def fetch_search(client, query: str) -> list:
    return get(client, "/search/movie", query=query).get("results", [])[:20]

def fetch_top(client) -> list:
    return get(client, "/movie/top_rated", page=1).get("results", []) + get(client, "/movie/top_rated", page=2).get("results", [])[:10]

def fetch_trending(client) -> list:
    return get(client, "/trending/movie/week").get("results", [])

def fetch_popular(client) -> list:
    return get(client, "/movie/popular", page=1).get("results", [])

def fetch_details(client, mid: int) -> dict:
    return get(client, f"/movie/{mid}")

def movie_rows(movies: list[dict]) -> list[str]:
    return [
        f"{m.get('title', '?'):<46}"
        f"  {(m.get('release_date') or '')[:4] or '—'}"
        f"  ★ {m.get('vote_average') or 0:.1f}"
        for m in movies
    ]

def show_details(d: dict):
    title = d.get("title", "?")
    year = (d.get("release_date") or "")[:4] or "—"
    rating = d.get("vote_average") or 0
    votes = d.get("vote_count") or 0
    runtime = d.get("runtime") or 0
    rt = f"{runtime // 60}h {runtime % 60}m" if runtime else "—"
    genres = ", ".join(g["name"] for g in d.get("genres", [])) or "—"
    tagline = d.get("tagline") or ""
    overview = d.get("overview") or "No overview available."

    clear()
    print(f"  {title} ({year})")
    if tagline:
        print(f"  {tagline}")
    print()
    print(f"  ★ {rating:.1f}/10   ({votes:,} votes)   {rt}")
    print(f"  {genres}")
    print()
    print(textwrap.fill(overview, width=72, initial_indent="  ", subsequent_indent="  "))
    print()
    input("  Press enter to go back…")

def screen_list(client: httpx.Client, movies: list[dict], prompt: str):
    if not movies:
        clear()
        print("No results.")
        input("Press enter…")
        return
    rows = movie_rows(movies)
    while True:
        clear()
        chosen = fzf(rows, prompt=prompt)
        if not chosen:
            return
        idx = next((i for i, r in enumerate(rows) if r == chosen), None)
        if idx is None:
            return
        clear()
        print("Loading…")
        show_details(fetch_details(client, movies[idx]["id"]))

def screen_search(client: httpx.Client):
    clear()
    query = input("Search: ").strip()
    if not query:
        return
    clear()
    print("Searching…")
    screen_list(client, fetch_search(client, query), prompt=f"Results: {query}")

MENU = [
    "  Search",
    "  Top 50",
    "  Trending",
    "  Popular",
    "  Quit",
]

def main():
    require_fzf()
    token = get_token()
    client = httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=15)

    with client:
        while True:
            clear()
            chosen = fzf(MENU, prompt="")
            if not chosen or "Quit" in chosen:
                clear()
                break
            elif "Search" in chosen:
                screen_search(client)
            elif "Top 50" in chosen:
                screen_list(client, fetch_top(client), "Top 50")
            elif "Trending" in chosen:
                screen_list(client, fetch_trending(client), "Trending")
            elif "Popular" in chosen:
                screen_list(client, fetch_popular(client), "Popular")

if __name__ == "__main__":
    main()
