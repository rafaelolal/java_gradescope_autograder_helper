from setuptools import find_packages, setup

with open("java_gradescope_auto_grader_helper/README.md", "r") as f:
    long_description = f.read()

setup(
    name="java-gradescope-auto-grader-helper",
    version="0.1.5",
    description="A helper package for setting up Gradescope autograder tests for Java projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="Rafael Almeida",
    author_email="contact@ralmeida.dev",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    package_data={
        "java_gradescope_auto_grader_helper": ["checkstyle/*"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "java_gradescope_auto_grader_helper=java_gradescope_auto_grader_helper.cli:main"
        ]
    },
    extras_require={
        "dev": ["twine>=6.1.0", "setuptools>=59.6.0"],
    },
    python_requires=">=3.10.6",
)
