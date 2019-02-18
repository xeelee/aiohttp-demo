# aiohttp-demo

## Description

`asyncio` based application providing basic "url shortener" functionality.

## Usage

### Run the application

Using docker container.

```
$ cd docker
$ docker-compose up app
```

### See API documentation

Swagger UI.

Open url in a web browser http://localhost:8008/api/doc


### Execute tests

Unit and integration ones.

```
$ cd docker
$ docker-compose run app py.test tests
```

### Get into container shell

```
$ cd docker
$ docker-compose run app bash
```

### Get into mongodb shell

```
$ cd docker
$ docker exec -it aiohttp-demo-mongodb bash
# mongo -uroot -ptoor
```

## TODO

What is missing.

* better password security
* session storage with encryption
* application usage stats
* better unit tests coverage
* refactoring in certain places (like i.e. list pagination)
* depencency injection container
* performance optimization
* automated functional tests
