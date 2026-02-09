# Best of Twitter

A lightweight, static site with a searchable archive of good tweets. (I didn't curate the tweets.)

## Why

I am trying to get better at Python, so I thought I'd try this as an exercise. I did none of the content work. This is just for education.

## Features

- Client-side search over a JSON dataset with 2.5k entries
- Single-tweet page with metadata and screenshots
- Images optimized as WEBP
- Minimal styling using Bootstrap
- Minimal external libraries
- Python helper to generate sitemap
- Minified JSON file

## Assembly

Here's how I did it

- Went to https://bsky.app/profile/threadotweets.bsky.social
- Scrolled down until everything loaded
- Saved complete page
- Wrote python to build rough draft of JSON with name, alt, and image URL for each tweet (note: Dennis included alt text on everything, like a saint) – used 4d0 for ID convention
- Converted images to WEBP at 85 quality and renamed to match corresponding ID
- Tried and failed to use OCR to extract dates for posts that show them
- Minified JSON
- Built client-side search
- Built single-tweet page
- Added some dynamic meta overwriting
- Generated sitemap using python

## Next Steps

- I could bring in new sources of good tweets to expand the data.
- I could clean the data – there are some missing names/handles.
- I may try again to use OCR to get dates or other missing data.

## Credits

The tweet collection was entirely curated by Dennis B. Hooper. I just wanted to see if I could scrape and clean the data as a personal project.

## License

Public domain. See the Unlicense.

## Author

it's ya boy pete
