## Hashworth: Field Duplicate Finder

## About:
This addon generates a hash value (MD5) for the selected field. Each field is processed and stripped of punctuation, pronouns, whitespace, etc... The checksum is used to search for duplicates in other notes/models that may have a different structure.

So, to illustrate:  
```"My ball.", "my balls!", "your ball?", "Your balls...", "Johny's Ball"```  
Except for the last one, the first four are all duplicates after processing.


## Tag Management:
You may also need these additional addons in order to manage the tags:  

Hierarchical Tags: https://ankiweb.net/shared/download/1089921461  

Using regexps to remove tags: https://ankiweb.net/shared/info/1502698883  


## Screenshots:

<img src="https://github.com/lovac42/Hashworth/blob/master/screenshots/dialog.png?raw=true">  

<img src="https://github.com/lovac42/Hashworth/blob/master/screenshots/browser.png?raw=true">  

## API Used:
Porter2-stemmer by Evan Dempsey, https://github.com/evandempsey/porter2-stemmer

