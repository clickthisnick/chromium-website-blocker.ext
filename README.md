# Simple Chromium Block Website Extension.

## Init

### To create block files (They are .gitignored)

bash init.sh

## To Install

Chrome -> More Tools -> Extensions -> Load Unpacked -> Load the `src` directory of this repo.

## Make better

You can hide extensions in Chrome

## Examples

### regexBlock.txt

https://www.example.com/foo\\?.*&bar=baz&.*

### blockedRequestInitiator.txt

https://www.example.com": "true