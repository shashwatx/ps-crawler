# Introduction

Crawls Playstore reviews using Selenium.

**Note:** Some reviews are trimmed and terminate with _...Full Review_ (which is a _button_ element).
I have modified the script to do the following right before dumping the reviews to file.
 1. Find all "Full Review" buttons.
 2. For each button
     1. scroll to bring the button in viewport.
     2. click on button.

## Required packages

Package | Version | Description
---- | ----|-------
[coloredlogs](https://pypi.org/project/coloredlogs/)|7.3| Logging
[selenium](https://pypi.org/project/selenium/) |3.141.0| Web Driver 
[bs4](https://pypi.org/project/beautifulsoup4/) |4.7.1| HTML Parser 
[click](https://pypi.org/project/click/) |7.0| Command line args
[time](https://docs.python.org/2/library/time.html) |n/a| Time related functions
[csv](https://docs.python.org/2/library/csv.html) |1.0| CSV operations
[os](https://docs.python.org/2/library/os.html) |n/a| File system utils 
[logging](https://docs.python.org/2/library/logging.html) | 0.5.1.2 | Logging
[re](https://expressjs.com/) |2.2.1| Regex operations

## Show Usage 
```
python crawler.py --help
```

### Example
```
python crawler.py -i ./input.txt -o data/ -d ./assets/chromedriver_linux64
```
