# Java Gradescope Autograder Helper

A tool for creating, running, and packaging Java autograders for Gradescope.

[![PyPI license](https://img.shields.io/pypi/l/java-gradescope-autograder-helper.svg)](https://pypi.org/project/java-gradescope-autograder-helper/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/java-gradescope-autograder-helper.svg)](https://pypi.org/project/java-gradescope-autograder-helper/) [![PyPI version](https://badge.fury.io/py/java-gradescope-autograder-helper.svg)](https://badge.fury.io/py/java-gradescope-autograder-helper) [![Downloads](https://pepy.tech/badge/java-gradescope-autograder-helper)](https://pepy.tech/project/java-gradescope-autograder-helper) [![Downloads](https://pepy.tech/badge/java-gradescope-autograder-helper/month)](https://pepy.tech/project/java-gradescope-autograder-helper) [![Downloads](https://pepy.tech/badge/java-gradescope-autograder-helper/week)](https://pepy.tech/project/java-gradescope-autograder-helper)

<!-- [![Downloads](https://pepy.tech/badge/java-gradescope-autograder-helper/day)](https://pepy.tech/project/java-gradescope-autograder-helper) -->

More easily and quickly create and test Gradescope autograders for Java assignments. By leveraging a reference solution and standard output, there is no need to hard code test cases. And, with a Python config file, you get the full benefits of writing tests in an easy-to-use coding language.

[PyPi](https://pypi.org/manage/project/java-gradescope-autograder-helper/releases/)
[GitHub](https://github.com/rafaelolal/java_gradescope_autograder_helper)

## Installation

`pip install java-gradescope-autograder-helper`

## Quick Start


1. Initialize the Gradescope environment locally: `autograder init`.
2. Put reference solution with a `main(String[] args)` entry point and any other required files in `autograder/source/`.
3. Edit `autograder/source/tests.py`.
4. Put an example student submission in `autograder/submission/`.
5. Test by navigating to `/autograder` and running `autograder run tests.py`.
6. Check results in `autograder/results/results.json`.
7. Zip the contents inside `autograder/source/` by runinng `autograder zip` and upload to Gradescope.


The whole flow for working with this package rests on the structure Gradescope creates in the docker containers it spins up for each student submission. Having that structure locally allows you to quickly iterate without depending on uploading it to Gradescope. You can refer to the [Gradescope autograder file hierarchy documentation](https://gradescope-autograders.readthedocs.io/en/latest/specs/#file-hierarchy) for more information on how/why the autograder is structured this way.

More comprehensive documentation is available under the Examples section.

## Commands

* `autograder` - Display the help menu.
* `autograder init` - Initialize the Gradescope environment in current directory.
* `autograder run <tests.py>` - Run the autograder locally.
* `autograder zip` - Zip the contents inside `autograder/source/` when in base directory.

## Features

The motivation for this package came after noticing the countless hours my professors had to spend creating Gradescope autograders for Java assignments. Additionally, I could not find packages that did exactly what I wanted online. I needed something with comprehensive documentation, that did not require much configuration. This package aims to provide a solution to these problems.

* No need to hardcode test cases, simply provide a reference solution.
* Independent of reference or student submission file structure, as long as it has the appropriate `main(String[] args)` entry point.
* Easily test autograder locally.
* Create custom functions for more versatility when testing student output.
* Test student syntax with Checkstyle by providing a custom config. You can edit or extend the default config by downloading it at: [GitHub/bowdoin_checks](https://github.com/rafaelolal/java_gradescope_autograder_helper/blob/main/src/java_gradescope_autograder_helper/checkstyle/bowdoin_checks.xml).
* Create custom style evaluation functions.
* Easily package to uplaod to Gradescope.
* Comprehensive documentation and examples.
* Easily extensible because it uses a `.py` file for the configuration.

## Examples

A comprehensive example is available on every execution of `autograder init`. Additionally, all generated files contain small descriptions and references to their purpose in the original Gradescope documentation.

Here is a sample of what `autograder init` generates: [GitHub/examples](https://github.com/rafaelolal/java_gradescope_autograder_helper/tree/main/src/java_gradescope_autograder_helper/examples).

The most important file is `autograder/source/tests.py`. This file contains all the configurations for the autograder and the test cases that will be run on the reference and student solutions.
