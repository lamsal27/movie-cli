const readline = require('readline');
const axios = require('axios');
const cheerio = require('cheerio');
const puppeteer = require('puppeteer');
const { spawn } = require('child_process');

const HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
};

function askQuestion(query) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    return new Promise(resolve => rl.question(query, ans => {
        rl.close();
        resolve(ans);
    }));
}

async function searchIMDb(title) {
    const url = `https://v2.sg.media-imdb.com/suggestion/${title[0].toLowerCase()}/${title.toLowerCase().replace(/ /g, '_')}.json`;
    const res = await axios.get(url, { headers: HEADERS });
    const results = res.data.d || [];
    return results.filter(r => r.id && r.l && r.y).slice(0, 5);
}

async function chooseMovie(movies) {
    console.log('\n Top Results:\n');
    console.log('  No  Title                              Year     IMDb ID');
    console.log('  --  ---------------------------------  -------  -------------');

    movies.forEach((m, i) => {
        console.log(`  ${i + 1}   ${m.l.padEnd(33)}  ${String(m.y || 'N/A').padEnd(7)}  ${m.id}`);
    });

    const choice = parseInt(await askQuestion('\n  Select a movie (1-5): '));
    return movies[choice - 1].id;
}

async function getIframeSrc(imdbId) {
    const url = `https://vidsrcme.vidsrc.icu/embed/movie?imdb=${imdbId}&autoplay=1`;
    const res = await axios.get(url, { headers: HEADERS });
    const $ = cheerio.load(res.data);
    const iframe = $('iframe').attr('src');
    if (!iframe) throw new Error('No iframe found.');
    return iframe.startsWith('//') ? 'https:' + iframe : iframe;
}

async function extractM3U8Link(iframeUrl) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(iframeUrl, { waitUntil: 'networkidle2' });
  await new Promise(resolve => setTimeout(resolve, 1000));
await page.evaluate(() => loadIframe());
  page.on('request', request => {
    const url = request.url();
    if (url.includes('.m3u8')) {
      link = url;
    }
  });
  console.log(" Searching the best quality...");
  await new Promise(resolve => setTimeout(resolve, 5000));
  await browser.close();
	return link;
   // return Array.from(m3u8Links)[0];
}


function playInMPV(link) {
    console.log('\n Launching player...\n');
    const mpv = spawn('mpv', ['--quiet', '--no-terminal', link], { stdio: 'inherit' });

    mpv.on('exit', (code) => {
        if (code !== 0) console.error(`mpv exited with code ${code}`);
    });
}

(async () => {
        const title = await askQuestion('\nEnter movie title: ');
        const results = await searchIMDb(title.trim());
        if (!results.length) {
            console.log('No results found.');
            return;
        }

        const imdbId = await chooseMovie(results);
        console.log(`\n Selected IMDb ID: ${imdbId}\n`);

        const iframeURL = await getIframeSrc(imdbId);
        console.log(' Movie page accessed successfully.');

        const streamURL = await extractM3U8Link(iframeURL);
        if (streamURL) {
            playInMPV(streamURL);
        } else {
            console.log('\n Sorry, Unable to fetch stream at the moment.');
            console.log(' Watch here instead:', iframeURL);
        }
})();

