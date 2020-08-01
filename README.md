# A simple comic crawler to crawl comic from https://comicbus.com/.

## Code Structure
![](https://i.imgur.com/OaCvJWA.png)

## To execute

1. Create a request file to download comics, example:

```json
{
    "食戟之靈": {
        "01話":[],
        "02話":[],
        "03話":[],
        "04話":[]
    }
}
```

2. Create a db file to restore the comic's image url, example:
```json
{
}
```

3. Execute the sample script
### Scrape comic website directly
```shell
$ ./src/basic_main.py [request_file.json] scripts [db.json]
```

### Scrape comic website through a well managed worker
a. download and follow the instruction of the README.md at [schedular](https://github.com/KeepLearningFromSideProject/scheduler) to start a worker service

b. run the script for worker of [schedular](https://github.com/KeepLearningFromSideProject/scheduler)
```shell
$ ./src/worker_main.py [request_file.json] scripts [db.json] http://0.0.0.0:5000/execute
# Notice that the url 'http://0.0.0.0:5000/execute' is the url for "shedular" to run as default,
# please just set this argument based on your real environment.
```

