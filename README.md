# Labyrinth Repository Search

[![SearchRepos](https://github.com/CERTCC/labyrinth/actions/workflows/repo_search.yml/badge.svg)](https://github.com/CERTCC/labyrinth/actions/workflows/repo_search.yml)
[![Update Summaries Daily](https://github.com/CERTCC/labyrinth/actions/workflows/update_summaries_daily.yml/badge.svg)](https://github.com/CERTCC/labyrinth/actions/workflows/update_summaries_daily.yml)

"Things are not always what they seem in this place, so you can't take anything for granted." - The Worm

This is an experimental project by the CERT/CC to find code that looks like it might be exploit code.

- Raw search results are placed into [`/results`](./results/), organized by year, month, and day.
- We periodically do a deep dive into the repositories found in our search results to see if any files contain strings that look like vulnerability identifiers.
Those results go into [`/data`](./data/), and are organized by repository IDs and vulnerabilty IDs.

This project is creating an index with pointers to repositories of potential interest to vulnerabilty analysts and security researchers.

## Important notes

Because we are basically just doing keyword searches to find repositories and then using regexes to match ID patterns in the repositories we found, we can't make any specific claims about any particular finding.

Labyrinth is _known_ to find 
- repositories that aren't security related at all (e.g., A repository with the description "This project exploits the law of large numbers" would be a valid find for the top-level search results.) 
- repositories that are meant to be exploits but not for what they say they are. Be wary: HoneyPoCs are a thing, and they definitely exist within the data set we've collected so far.
- repositories that are intended to distract security analysts who rely too much on search strings and pattern matching (_irony noted_)
- repositories that contain lists of known vulnerabilities, exploits, or detection signatures for either
- repositories that are collections of exploits (there sure are a lot of clones of ExploitDb and Metasploit Framework out there)
- repositories that are work-in-progress, broken, or otherwise abandoned attempts at exploit development
- repositories that are short-lived and might be gone by the time you go to look at them again
- repositories that contain actual exploits

We consider many of these to be *noise* in the data collected (except for the known exploit collections of course). However, this data is intended to serve as the front end of an analysis pipeline and not the finished product. So while we're interested in improving the signal-to-noise ratio, we don't really consider it to be a big problem that needs to be fixed (for now at least). Improvement suggestions are welcome nonetheless.

All of this is meant to say that:

### Just because it's in Labyrinth doesn't mean there's a working public exploit for it.

But it might be worth a look.

## Why _Labyrinth_?

Because a large collection of code repositories can look from the outside like "a maze of twisty little passages, all alike".
And while not everything you come across is out to get you, sometimes there _are_ monsters lurking in the shadows.
