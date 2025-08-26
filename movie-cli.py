import os
import typer
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

def clean_title(title: str) -> str:
    return title.split(". ", 1)[-1] if ". " in title else title

def fetch_top_25():
    url = "https://www.imdb.com/chart/top/"
    res = requests.get(url, headers=BASE_HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    movies = []
    rows = soup.select(".ipc-metadata-list-summary-item")
    for row in rows[:25]:
        title_tag = row.select_one("h3")
        if not title_tag:
            continue
        title = clean_title(title_tag.get_text(strip=True))
        year = row.select_one(".cli-title-metadata span")
        duration = row.select_one(".cli-title-metadata span:nth-of-type(2)")
        rating = row.select_one(".ipc-rating-star--rating")
        imdb_link = row.select_one("a[href*='/title/']")
        imdb_id = imdb_link['href'].split("/")[2] if imdb_link else None

        movies.append({
            "title": title,
            "year": year.get_text(strip=True) if year else "N/A",
            "duration": duration.get_text(strip=True) if duration else "N/A",
            "rating": rating.get_text(strip=True) if rating else "N/A",
            "imdb_id": imdb_id
        })
    return movies

def fetch_most_popular():
    url = "https://www.imdb.com/chart/moviemeter/"
    res = requests.get(url, headers=BASE_HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    movies = []
    items = soup.select("li.ipc-metadata-list-summary-item")[:100]

    for item in items:
        title_tag = item.select_one("h3.ipc-title__text")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        link_tag = item.select_one("a.ipc-title-link-wrapper")
        imdb_id = link_tag['href'].split("/")[2] if link_tag and 'href' in link_tag.attrs else None

        metadata = item.select("div.cli-title-metadata span")
        year = metadata[0].get_text(strip=True) if len(metadata) > 0 else "N/A"
        duration = metadata[1].get_text(strip=True) if len(metadata) > 1 else "N/A"

        rating_tag = item.select_one("span.ipc-rating-star--rating")
        rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

        movies.append({
            "title": title,
            "year": year,
            "duration": duration,
            "rating": rating,
            "imdb_id": imdb_id,
        })
    return movies

def search_movies(query: str):
    url = f"https://www.imdb.com/find/?q={query}"
    res = requests.get(url, headers=BASE_HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    movies = []
    containers = soup.select(".ipc-metadata-list-summary-item__c")
    links = soup.select(".ipc-metadata-list-summary-item__c .ipc-metadata-list-summary-item__t")

    for idx, container in enumerate(containers):
        lines = container.get_text(separator="\n").split("\n")
        if len(lines) < 3:
            continue
        title, year, actors = lines[:3]

        imdb_href = links[idx]['href'] if idx < len(links) else ""
        imdb_id = imdb_href.split("/")[2] if imdb_href else None

        movies.append({
            "title": title.strip(),
            "year": year.strip(),
            "actors": actors.strip(),
            "imdb_id": imdb_id
        })

    return movies

def display_movies_table(movies, table_type="default"):
    table = Table(title="Movies")
    table.add_column("No", style="bold yellow")
    table.add_column("Title", style="bold cyan")
    table.add_column("Year", style="green")
    if table_type == "search":
        table.add_column("Actors", style="magenta")
    else:
        table.add_column("Duration", style="magenta")
        table.add_column("Rating", style="red")

    for i, m in enumerate(movies, start=1):
        if table_type == "search":
            table.add_row(str(i), m['title'], m['year'], m['actors'])
        else:
            table.add_row(str(i), m['title'], m['year'], m.get('duration','N/A'), m.get('rating','N/A'))
    console.print(table)

def fetch_movie_details(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}"
    res = requests.get(url, headers=BASE_HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.select_one('h1[data-testid="hero__pageTitle"]')
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    year_tag = soup.select_one('a[data-testid="title-details-releasedate"]') \
               or soup.select_one('ul.ipc-inline-list li a[href*="releaseinfo"]') \
               or soup.select_one('span.sc-8c396aa2-2')
    year = year_tag.get_text(strip=True) if year_tag else "N/A"

    runtime_tag = soup.select_one('li[data-testid="title-techspec_runtime"] div') \
                  or soup.select_one('ul.ipc-inline-list li:nth-of-type(3)')
    runtime = runtime_tag.get_text(strip=True) if runtime_tag else "N/A"

    rating_tag = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating"] span[class*="sc-"]')
    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
    votes_tag = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating"] div[class*="sc-"]')
    votes = votes_tag.get_text(strip=True) if votes_tag else "N/A"

    genres = [g.get_text(strip=True) for g in soup.select('div[data-testid="genres"] a')] \
             or [g.get_text(strip=True) for g in soup.select('div.ipc-chip-list__scroller a')]
    genres_str = ', '.join(dict.fromkeys([g for g in genres if g])) or "N/A"

    directors = []
    stars = []
    credit_sections = soup.select('li[data-testid="title-pc-principal-credit"]')
    for sec in credit_sections:
        label = sec.select_one('span.ipc-metadata-list-item__label')
        names = [a.get_text(strip=True) for a in sec.select('a') if a.get_text(strip=True)]
        if not label:
            continue
        lbl = label.get_text(strip=True).lower()
        if 'director' in lbl:
            directors.extend(names)
        elif 'star' in lbl or 'stars' in lbl:
            stars.extend(names)

    if not directors or not stars:
        credit_rows = soup.select('section.ipc-page-section li[data-testid^="title-pc-principal-credit"]')
        for row in credit_rows:
            lbl = row.select_one('span.ipc-metadata-list-item__label')
            names = [a.get_text(strip=True) for a in row.select('a') if a.get_text(strip=True)]
            if not lbl:
                continue
            lbl_text = lbl.get_text(strip=True).lower()
            if 'director' in lbl_text and not directors:
                directors.extend(names)
            if ('star' in lbl_text or 'stars' in lbl_text) and not stars:
                stars.extend(names)

    directors = [d for d in directors if d]
    stars = [s for s in stars if s]

    plot_tag = soup.select_one('span[data-testid="plot-xl"]') or soup.select_one('div.plot_summary .summary_text')
    plot = plot_tag.get_text(strip=True) if plot_tag else "N/A"

    return {
        "title": title,
        "year": year,
        "duration": runtime,
        "rating": rating,
        "votes": votes,
        "directors": ', '.join(dict.fromkeys(directors)) if directors else "N/A",
        "genres": genres_str,
        "plot": plot
    }

@app.command()
def main():
    os.system('clear')

    console.print("\nChoose an option:", style="bold green")
    console.print("[1] Top 25 Movies")
    console.print("[2] Most Popular / Trending")
    console.print("[3] Search for a movie")

    option = typer.prompt("Enter option number", type=int)

    if option == 1:
        movies = fetch_top_25()
        table_type = "default"
    elif option == 2:
        movies = fetch_most_popular()
        table_type = "default"
    elif option == 3:
        search = typer.prompt("Enter movie title")
        movies = search_movies(search)
        table_type = "search"
        if not movies:
            console.print("No movies found.", style="bold red")
            raise typer.Exit()
    else:
        console.print("Invalid option.", style="bold red")
        raise typer.Exit()

    display_movies_table(movies, table_type=table_type)

    choice = typer.prompt(f"Enter movie number to watch (1-{len(movies)})", type=int)
    if choice < 1 or choice > len(movies):
        console.print("Invalid selection.", style="bold red")
        raise typer.Exit()

    selected_movie = movies[choice-1]
    imdb_id = selected_movie['imdb_id']

    details = fetch_movie_details(imdb_id)
    console.print(f"\nTitle: [bold cyan]{details['title']}[/bold cyan]")
    console.print(f"Released on: [green]{details['year']}[/green]")
    console.print(f"Duration: [magenta]{details['duration']}[/magenta]")
    console.print(f"IMDB Rating: [red]{details['rating']}[/red] ({details['votes']} votes)")
    console.print(f"Director(s): [cyan]{details['directors']}[/cyan]")
    console.print(f"Genres: [magenta]{details['genres']}[/magenta]\n")
    console.print(f"{details['plot']}\n")
    link = f"https://vidsrc.pm/embed/movie/{imdb_id}"
    console.print(f"Watch {details['title']} here: [cyan]{link}[/cyan]\n", style="bold green")

if __name__ == "__main__":
    app()

