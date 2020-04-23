[![Build Status](https://travis-ci.com/yshrdbrn/ogle.svg?token=VYwDyt1SvCzmweAX6xmw&branch=master)](https://travis-ci.com/yshrdbrn/ogle)
# ogle

Ogle is a compiler written in python from scratch. It compiles a language similar to C++ to the [MOON processor's](moon) assembly.

## Running the compiler
*Note:* The compiler is tested using Python 3.7

First, install all the required packages in your venv:
```shell script
$ pip install -r requirements.txt
```

Then, run `ogle/runner.py`:
```shell script
$ python3 ogle/runner.py <input_file_name>
```
The output `.m` file will be generated in the same directory as the input file (if there are not compilation errors).


## Running the tests
Tests are run using the `pytest` library. To run the tests, run `pytest` in the root directory:
```shell script
$ pytest
```