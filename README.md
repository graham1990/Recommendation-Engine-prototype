# Build a Recommendation Engine Prototype with Python

## Overview

This project is a prototype for a recommedation engine that uses Panda queries display on a Matplotlib UI.

A recomendation may be either based on
  1. explicit feedback such as a star rating, thumb-up/thumb-down
  2. implicit feedback such as the number of minutes watched or movie sequels / number of epsisodes watched.

There are two types of recommendation engine:

### Content-based: Show me more of the same of what I liked before.

In content-based filtering, the similarity between different products is calculated on the basis of the attributes of the products. For instance, in a content-based movie recommender system, the similarity between the movies is calculated on the basis of genres, the actors in the movie, the director of the movie, etc.

### Collaborative Filtering: Tell me what's popular among my neighbours, I also might like.

When a huge number of users have assigned the same ratings to movies X and Y, when a new user comes who has assigned the same rating to movie X but hasn't watched movie Y yet, will be recommended movie Y.

## Installation

### Windows
Open a command prompt or powershell and run the following commands, replacing 'project-root' with the path to the root folder of the project.
```
> cd 'project-root'
> python -m venv venv
> venv\Scripts\activate.bat
> pip install -r requirements.txt
```

### macOS
Open a terminal and run the following commands, replacing 'project-root' with the path to the root folder of the project.
```
$ cd 'project-root'
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
*Note: If you've installed Python 3 using a method other than Homebrew, you might need to type `python` in the second command instead of `python3`.*


## Types of prototypes used / proposed
Wireframe
Throwaway Prototyping
Evolutionary Prototyping
Incremental Prototyping

## Software prototypes checklist
  1. Investigate Content based and Collaborative Filtering
  2. Build importer that can take Excel as well as csv files and manage the various data formats being used.
  3. WIP: Extend importer to allow Json files from websites and other microservices
  4. WIP: Investigate correlations operation further
  5. TODO: Investigate Dimensional Modelling Technique, organizing data into dimensions and facts.
  6. TODO: Front end wire diagram

### Evolutionary Prototyping Throwaway prototype 1 
This rapid throwaway model will use Evolutionary Prototyping to produce the Content-based and Collaborative Filtering prototype. This will be incrementally refined and added to the following plan. This model is used because both the technology used in the project is new and not well understood, as well as the software requirement is far from being understood or stable at this initial stage.
The evolutionary steps will be:
  1. Load the movie data file
  2. Load the movie ratings data and merge with the movies
  3. Clean data: Remove values which represent no data
  4. Identify data from specfic movies and reviews
  5. Produce basic statistics i.e. averages, total count etc
  6. Summarise how many reviews each movie has
  7. Merge local preferences with combined movie data
  8. Add column to to the combined data
  9.  TODO: Investigate Label encoding
  10. Find out correlation in movie data
  11. Enable the ability for year query, through data manipulation
  12. Clean Data: Modify title so that title can be searched for without year


#### Evaluation
The prototype has had to focus on explicit Collaborative Filtering, due to the limited nature of the available dataset preventing Content-based.

The shape of the data as well as the content was important, with Pandas during correlation reporting the shape was incorrect. This was not a problem with that data but is an issue when there are insifficent data to correlate, but failed to produce results, shown by a later prototype. Therefore the size or ability can be influenced by the size of the sample.
The Pearson's algorithm, with smaller value sets sometimes suggested a fairly linear relationship, even when there was none. This seems a spurious correlation which are correlations which are strong but observed purely due to chance, or randomness.

Pandas arithmetic did not throw divide by 0 exception but displayed warnings, so could not be used to detect such issues where result were INF. For correct interpretation data types are important and different between libraries, making it harder to other libraries to use the Pandas data. Runtime slice warnings from numpy also need investigating.

Modifying the data for a historical based recommendation, though, an extra column, the device type. This had data for two viewing ratings by the same user, which would need considering which to use.Despite the low sample size there appears to be a correlation between rating being higher on a second viewing. On closer inspection the two ratings could be causally independent, being dependent upon later experience (of the later review) and / or watching on a different device, therefore, to prevent confounding, relationships that are not real must be avoided. This brought about the relisation that Correlation does not imply causality.

Issues with fields where more than one type of information in a field required fixing by conversion functions. In one case conversion was required to allow axis to be display as intended, using matplotlib. Problems also exist with amounts with currencies or titles with dates which can easily occur until the data is cleaned.

The Collaborative Filtering data modeling has shown that data is key and to statisfy the initial requirement from the Google data is impossible. Therefore Google data would need suplementing with data from multiple sources / websites i.e IMDb as well as Google. Research showed that IMDb has user ratings, critics ratings and links to external site ratings where the reviews are Qualitative only rather than Quantitative and Qualitative. Some Qualitative data was seen to contain contain useful tags, however transitory tags i.e. Trending Now, Award-Winning Comedies and Continue Watching tags would be seen to be benefical. Only one type of ratings where considered in this prototype and the only tags where genre which fully research suggested should be used as an encoded form only.

It was likely that tags identifying attributes in the movie would need to be much more comprehensive and interlinked to reflect say "comedy historical Korean drama". This will require an and function but also needs to give matches when not all tags have been found.

### Incremental prototype 2
The abstract factory pattern was used as the basis of importing data to different data types. The template pattern was used to ensure that all table types were processed in a consistant manner using shared code.
A further enchancement is intended to handle CSV files using different codecs at a later stage, along with an ability to download straight to a NUMPY data stream to allow both developer friendly data analysis using Pandas and production ready solutions using numpy.

### Incremental prototype 3
This is WIP, which is going to import primarly JSON data from a website where failure is likely. The incremental prototype starts with a retry function so that the function is truely reusable and  any data importes do not become unreliable. There are three models implemented; basic Coefficient Backoff, Exponential Backoff and jitter. The jitter function accepts the random integer function as an optional keyword argument allowing alternative random number generators to be used and to aid automating testing.

Retry uses dependency inversion, and the builder pattern with a fluent interface to chain methods together.The API is not a decorator, but a Python context manager, so that the function in the program is more expecit. The return is a detailed log of when the retry occurred and what results where obtained from the function being returned, so that retries can be assessed for their impact on a system. The code run can be a method or lambda code.

Intended is to add fuzzing for test purposes. Fuzz testing or fuzzing is an automated software testing method that injects invalid, malformed, or unexpected inputs in an attempt to find vulnerabilities or crash-causing inputs. Some examples of vulnerabilities that can be found by fuzzing are SQL injection, buffer overflow, denial of service and cross-site scripting attacks. A fuzzing tool injects these inputs into the system and then monitors for exceptions such as crashes or information leakage, which is why good record keeping of returns and times is required, so that crashes are less difficult to analyze and reproduce.

To test jitter a psuedeo random generator was buit. This is adapted to look just like random int in usage to the module. This allowed TTD development of the jitter routine without merely substituting a single number. This uses a Python generator with an iterator built-in all contained in a module which can be imported to replace random functionally. This also means there is no need to use the Singleton or Borg pattern as one single source of data is provided, through the module import.

### Incremental prototype 4
This is WIP. As the understanding of correlations needed further work, particularly the correlation algorithms; an incremental prototype was built to investigate correlations operation further. This will allow the correlation types to be developed individually, evaluated and merged into a final build later.

#### Evaluation
As can be seen the Correlation ration and Cramer's V (orginal) work well at working out the array has a constant offset + and -, however the improved Cramer's V produces a divide by 0 warning, probably due to the high correlation of the data. The data provide was set of data with a set of random offsets added and the same offsets subtracted. The 2 methods of correlation between a categorical column and a numeric column (Correlation ration) and the correlation between two categorical columns (Cramer's V) both identified the items as highly correlated.
The first 2 methods, Linear correlation between two sets of numeric data (Pearson) and the linear correlation between the ranks of two sets of numeric data (Spearman) still suggested a reasonably high correlation of around 0.7. This was found to be consistent on every run which indicates an issue with the random number generator being restarted each run.
