# Resume Analysis Labs!

## How it Works

1. **Upload**: Simply upload a resume file or provide a URL link to initiate the analysis.
2. **Processing**: The system extracts text from the resume, converts it into a structured format, and cleans/preprocesses the data.
3. **Analysis**: It calculates various criteria based on the processed data.
4. **Aggregation**: Criteria are aggregated into a single score using a weighted mean.
5. **Level Mapping**: The score is mapped to predefined level ranges, indicating the expertise level of the candidate.

## Year of Experience (YoP) Scale

The Year of Experience (YoP) scale quantifies experience in terms of years, with each year equivalent to 10 points. This scale provides a standardized measure for evaluating candidates' experience levels, facilitating a fair and objective assessment process.

in the folloing example we could see how other qualifications are converted to YoP:

| Qualification                                     | Calculation                                  | Points | YoP  |
| ------------------------------------------------- | -------------------------------------------- | ------ | ---- |
| 5 years working as junior developer               | 5 years \* 10 (Junior)                       | 50     | 5    |
| 2 years working as mid-level developer            | 2 years \* 20 (Mid)                          | 40     | 4    |
| 1 degree in Computer Science                      | 1 degree \* 10                               | 10     | 1    |
| 1 year working as team leader in a simple project | 1 year \* 5 (contribution) \* 2 (complexity) | 10     | 1    |
| 2 certificates in Data Science                    | 2 certificates \* 2.4                        | 4.8    | 0.48 |

Since using same scale for all qualifications, we can easily compare them and calculate the total score.

- 1 year of Mid-level experience is equal to 2 years of Junior-level experience.
- 1 degree is equal to 1 year of experience.
- 1 certificate is equal to 0.2 years of experience.
- 1 year working in a large project as a team leader (5\*5) is equal to 2.5 years of experience.

So far, we could easily tweak the scale by changing the weights of each qualification and the score range for each level.

Finaly, we could map the total score to a predefined level range, indicating the expertise level of the candidate.

## Overview of Criteria and Scoring

| Criteria            | Description                                             | Calculation                                                                |
| ------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- |
| Work Experience     | Total number of years of work experience                | Each year contributes 10 points                                            |
| Project Experience  | Evaluation based on project complexity and contribution | Complexity (1-5), Contribution (1-5)                                       |
| Employment Duration | Total employment duration, with weighted positions      | Levels: Intern (0.5), Junior (1), Mid (2), Senior (3), Lead (4), Chief (5) |
| University Degrees  | Each degree contributes 1 Year of Experience (YoP)      | Each degree = 1 YoP = 10 points                                            |
| Certificates        | Each certificate contributes 0.2 YoP                    | Each certificate = 0.2 YoP = 2.4 points                                    |

## Score Ranges and Explanation

| Level     | Score Range |
| --------- | ----------- |
| Intern    | 0-9         |
| Fresher-  | 10-14       |
| Fresher   | 15-19       |
| Fresher+  | 20-24       |
| Junior-   | 25-31       |
| Junior    | 32-38       |
| Junior+   | 39-44       |
| Middle-   | 45-51       |
| Middle    | 52-58       |
| Middle+   | 59-67       |
| Senior-   | 68-77       |
| Senior    | 78-87       |
| Senior+   | 88-97       |
| Principal | 98+         |

## Usage

To run the app locally, execute `streamlit run app.py` in your terminal.

## Acknowledgments

Thank you for visiting the labs page. Contributions and feedback are welcome!
