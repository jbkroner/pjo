[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# `pjo` 
`pjo` is a Python port of [`jop`](https://github.com/jpmens/jo)!  It is _mostly_ compatible with original `jo` options and arguments.    

`pjo` is a simple json encoding utility for bash. 

You can create json objects:  
```bash
$ pjo -p name=pjo n=17 parser=false
{
    "name": "pjo",
    "n": 17,
    "parser": false
}
```
or arrays: 
```bash
$ pjo -a 1 2 3 4
[1,2,3,4]
```

It also supports nested objects: 
```bash
$ pjo -p nested=$(pjo myKey=someValue)
{
   "nested": {
      "myKey": "someValue"
   }
}
```

It has some simple options, and you can read [@jpmens](https://github.com/jpmens) original blogpost about jo (here)[https://jpmens.net/2016/03/05/a-shell-command-to-create-json-jo/]

## Build and install `pjo`
`pjo` was written and tested with Python 3.9.13.  It is not yet distributed via pypi so you must build and install it locally. 

Clone this repo and cd into it: 
```bash
git clone https://github.com/jbkroner/pjo.git
cd pjo
```

Create and acitvate a venv (optional): 
```bash
$ python3 -m venv venv
$ source ./venv/bin/activate
(venv)
```

Install requirements
```bash
(venv) $ pip install -r requirements.txt
```

upgrade pip
```bash
(venv) $ python3 -m pip install --upgrade pip
```

install the latest version of `build`, then build pjo
```
(venv) $ python3 -m pip install --upgrade build
(venv) $ python3 -m build
```

install for local development and usage: 
```
(venv) $ pip install -e .
```

# OPTIONS

*`pjo`* understands the following global options.

  - \-a  
    Interpret the list of *words* as array values and produce an array
    instead of an object.
  - \-B  
    By default, *`jo`* interprets the strings "`true`" and "`false`" as
    boolean elements `true` and `false` respectively, and "`null`" as
    `null`. Disable with this option.
  - \-D  
    Deduplicate object keys.
  - \-e  
    Ignore empty stdin (i.e. don't produce a diagnostic error when
    *stdin* is empty)
  - \-p  
    Pretty-print the JSON string on output instead of the terse one-line
    output it prints by default.
  - \-v  
    Show version and exit.
  - \-V  
    Show version as a JSON object and exit.

Read element values from files: a value which starts with `@` is read in
plain whereas if it begins with a `%` it will be base64-encoded and if
it starts with `:` the contents are interpreted as JSON:

    $ pjo program=pjo authors=@AUTHORS
    {"program":"pjo","authors":"firstname lastname <randomemail@email.com>"}
    
    $ pjo filename=AUTHORS content=%AUTHORS
    {"filename":"AUTHORS","content":"SmFuLVBpZXQgTWVucyA8anBtZW5zQGdtYWlsLmNvbT4K"}
    
    $ pjo nested=:nested.json
    {"nested":{"field1":123,"field2":"abc"}}

These characters can be escaped to avoid interpretation:

    $ pjo name="James Kroner" twitter='\@jameskroner'
    {"name":"James Kroner","twitter":"@jameskroner"}
    
    $ pjo char=" " URIescape=\\%20
    {"char":" ","URIescape":"%20"}
    
    $ pjo action="split window" vimcmd="\:split"
    {"action":"split window","vimcmd":":split"}







## Options and examples
