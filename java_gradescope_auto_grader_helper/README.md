# Java Gradescope Auto Grader Helper

1. Write documentation
2. Create startup example
3. Send to the prof the new starting code for students
4. Change this to use UV
5. Fix other projects to work with this

## Setup

**setup.sh**: a setup (Bash) script that installs all your dependencies. By default, we're running on Ubuntu images, so you can use apt, or any other available means of setting up packages.

**run_autograder**: an executable script, in any language (with appropriate #! line), that compiles and runs your autograder suite and produces the output in the correct place.


## Working Directory

When the autograder executes, the working directory is **/autograder.**

Files you provide:

**/autograder/source** contains the extracted contents of your autograder zip file.
**/autograder/run_autograder** is where your autograder script gets copied to during the Docker image build process.
**/autograder/results/results.json** is where you put the test output that is uploaded to Gradescope. This must be produced as a result of executing run_autograder.

## Grading

Our autograder harness downloads the student's submission and puts it in **/autograder/submission**,

and then runs **/autograder/run_autograder**.

Once run_autograder has finished running, the harness checks for output in **/autograder/results/results.json**, and uploads these results to Gradescope.

Output format

```
{ "score": 44.0, // optional, but required if not on each test case below. Overrides total of tests if specified.
  "execution_time": 136, // optional, seconds
  "output": "Text relevant to the entire submission", // optional
  "output_format": "simple_format", // Optional output format settings, see "Output String Formatting" below
  "test_output_format": "text", // Optional default output format for test case outputs, see "Output String Formatting" below
  "test_name_format": "text", // Optional default output format for test case names, see "Output String Formatting" below
  "visibility": "after_due_date", // Optional visibility setting
  "stdout_visibility": "visible", // Optional stdout visibility setting
  "extra_data": {}, // Optional extra data to be stored
  "tests": // Optional, but required if no top-level score
    [
        {
            "score": 2.0, // optional, but required if not on top level submission
            "max_score": 2.0, // optional
            "status": "passed", // optional, see "Test case status" below
            "name": "Your name here", // optional
            "name_format": "text", // optional formatting for the test case name, see "Output String Formatting" below
            "number": "1.1", // optional (will just be numbered in order of array if no number given)
            "output": "Giant multiline string that will be placed in a <pre> tag and collapsed by default", // optional
            "output_format": "text", // optional formatting for the test case output, see "Output String Formatting" below
            "tags": ["tag1", "tag2", "tag3"], // optional
            "visibility": "visible", // Optional visibility setting
            "extra_data": {} // Optional extra data to be stored
        },
        // and more test cases...
    ],
  "leaderboard": // Optional, will set up leaderboards for these values
    [
      {"name": "Accuracy", "value": .926},
      {"name": "Time", "value": 15.1, "order": "asc"},
      {"name": "Stars", "value": "*****"}
    ]
}
```

## Advanced Meta Data

```json
The file /autograder/submission_metadata.json contains information about the current and previous submissions. It contains the following information:

{
  "id": 123456, // Unique identifier for this particular submission
  "created_at": "2018-07-01T14:22:32.365935-07:00", // Submission time
  "assignment": { // Assignment details
    "due_date": "2018-07-31T23:00:00.000000-07:00",
    "group_size": 4, // Maximum group size, or null if not set
    "group_submission": true, // Whether group submission is allowed
    "id": 25828, // Gradescope assignment ID
    "course_id": 1234, // Gradescope course ID
    "late_due_date": null, // Late due date, if set
    "release_date": "2018-07-02T00:00:00.000000-07:00",
    "title": "Programming Assignment 1",
    "total_points": "20.0" // Total point value, including any manual grading portion
  },
  "submission_method": "upload", // Can be "upload", "GitHub", or "Bitbucket"
  "users": [
    {
      "email": "student@example.com",
      "id": 1234,
      "name": "Student User"
    }, ... // Multiple users will be listed in the case of group submissions
  ],
  "previous_submissions": [
    {
      "submission_time": "2017-04-06T14:24:48.087023-07:00",// previous submission time
      "score": 0.0, // Previous submission score
      "autograder_error": true|false // If true, this submission failed to run at no fault of the student.
      "results": { ... } // Previous submission results object, ONLY for the latest previous submission.
    }, ...
  ]
}
```