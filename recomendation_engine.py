import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import json
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re



def load_data_from_csv(csv_name):
    df_data = pd.read_csv(csv_name, na_values=missing_values)
    print("{} Shape:", df_data.shape)
    print(df_data.head())
    return df_data


def save_date_to_csv(df_data, csv_name):
    df_data.to_csv(csv_name, index=None)


def extract_year(movies_df):
    """Where possible, transform the data to give a seperate searchable release year column.
    Most movie titles have a year in title, so remove this date and place in it's own column
    """
    # Specify the parentheses so we don't conflict with movies that have years in their titles.
    movies_df["year"] = movies_df["title"].str.extract(r"\((\d\d\d\d)\)").fillna("")
    # Force to numeric, where possible, so that min and max works
    movies_df["year"] = (
        movies_df["year"]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(movies_df["year"])
    )

    # Removing the years from the 'title' column.
    movies_df["title"] = movies_df["title"].apply(
        lambda x: re.sub(r"(\(\d\d\d\d\))", "", str(x))
    )
    # Applying the strip function to get rid of any ending white space characters that may have appeared, using lambda function.
    movies_df["title"] = movies_df["title"].apply(lambda x: x.strip())
    print(movies_df["year"])
    print(movies_df["title"])
    return movies_df


def genres_to_list(movies_df):
    """Every genre is separated by a pipe, so split into list."""
    movies_df["genres"] = movies_df.genres.str.split("|")
    return movies_df


def read_json(filename):
    # Read from JSON data source
    return pd.read_json(filename)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


# Use local configuration data, in this case local preferences
# (which happen to be in the same format as reviews)
print("My personal preferences")
df_my_reviews = pd.DataFrame(
    {
        "userId": [5000000, 5000000, 5000000],
        "movieId": [1, 3, 1],
        "rating": [1.0, 4.0, 3.8],
        "timestamp": [964981247, 964982703, 964982703],
    }
)
print(df_my_reviews)

# Defining additional NaN identifiers.
missing_values = ["na", "--", "?", "-", "None", "none", "non"]

print("Movie reviews downloaded")
# df_reviews = pd.read_csv("https://storage.googleapis.com/neurals/data/data/reviews.csv")
df_reviews = pd.read_csv("reviews.csv", na_values=missing_values)
# Preview the first 5 lines of the loaded data
print(len(df_reviews))
print("Movies_df Shape:", df_reviews.shape)
print(df_reviews.head())
# df_reviews.to_csv("reviews.csv", index=None)

print("Add online reviews to my personel reviews")
df_reviews = pd.concat([df_my_reviews, df_reviews])
# Preview the first 5 lines of the loaded data
print(df_reviews.head())
# Realign indexes from adding personal preferences
df_reviews.reset_index(drop=True, inplace=True)
print(df_reviews.head())

print("I also know what device I was using")
df_device = pd.DataFrame({"device": ["phone", "computer", "tv"]})
df_reviews = pd.concat([df_reviews, df_device], axis=1)
print(df_reviews.head())


print("Movie titles")
# df_movie_titles = pd.read_csv(
#     "https://storage.googleapis.com/neurals/data/data/movies.csv"
# )
# df_movie_titles = pd.read_csv("movies.csv", headers=None)
df_movie_titles = pd.read_csv("movies.csv", na_values=missing_values)
# Preview the first 5 lines of the loaded data
print(len(df_movie_titles))
print("Movies_df Shape:", df_movie_titles.shape)
print(df_movie_titles.head())
# df_movie_titles.to_csv("movies.csv", index=None)


print("Merged Movie data")
# Merging all the datasets
df = pd.merge(df_reviews, df_movie_titles, on="movieId")
print(df.head(10))
print(df.tail())

# Total number of ratings for a movie
print(df.groupby("title")["rating"].count().sort_values(ascending=False).head())


# Content based Insights from data
# Average of each movie
print("Average rating of each title")
# Get the average rating of each movie. To do so, we can group the dataset by the title of the movie and then calculate the mean of the rating for each movie.
df_ratings = pd.DataFrame(df.groupby("title")["rating"].mean())
# add the number of ratings for a movie to the dataframe
df_ratings["number_of_ratings"] = df.groupby("title")["rating"].count()
print(df_ratings.head())

# Can sort average ratings
print(df.groupby("title")["rating"].mean().sort_values(ascending=False).head())

# Filter rows and columns, by index
print("find by reference")
print(df_ratings.iloc[0:5])
print(df_ratings.iloc[2:7, 2:3])

plt.figure(figsize=(8, 6), label="No of Movie ratings")
plt.ylabel("# of ratings")
plt.xlabel("# of movies")
plt.rcParams["patch.force_edgecolor"] = True
df_ratings["number_of_ratings"].hist(bins=50)
plt.show()


plt.figure(figsize=(8, 6), label="Movie ratings score")
plt.ylabel("# of ratings")
plt.xlabel("Rating value")
plt.rcParams["patch.force_edgecolor"] = True
df_ratings["rating"].hist(bins=50)
plt.show()

plt.figure(figsize=(8, 6), label="No of ratings vs rating value")
plt.scatter(df_ratings["rating"], df_ratings["number_of_ratings"])
# plt.title("No of ratings vs rating value")
plt.ylabel("# of ratings")
plt.xlabel("Rating value")
plt.show()

# Structuring the collabration recommendations
movie_matrix = df.pivot_table(index="userId", columns="title", values="rating")

# it's not possible to compute a Pearson correlation (the default correlation method for corrwith) between Forrest Gump and movie X unless there are at least 2 users that have rated both Forrest Gump and movie X

# Remove users that have not rated Forrest Gump.
user_movie_rating = movie_matrix[movie_matrix.get("Forrest Gump (1994)").notnull()]

# Remove movies that don't have at least 2 ratings. After this, all movies will have at least 2 ratings from users that have also rated Forrest Gump, because after the previous step everyone has rated Forrest Gump.
user_movie_rating = user_movie_rating.dropna(axis="columns", thresh=2)

forrest_gump_ratings = user_movie_rating["Forrest Gump (1994)"]
forrest_gump_ratings.head()

movies_like_forest_gump = user_movie_rating.corrwith(
    forrest_gump_ratings, numeric_only=True
)

corr_forrest_gump = pd.DataFrame(movies_like_forest_gump, columns=["Correlation"])
corr_forrest_gump.dropna(inplace=True)
print(corr_forrest_gump.head())

print(user_movie_rating.head())
# nan_user_rating = df.loc[(df["rating"] > 0.9)]
# print(df.isnull().any(axis=1))
# print(nan_user_rating.head())
# print(nan_user_rating["title"].head())

print(df.to_numpy())
print(df["rating"].to_numpy())
json_dump = json.dumps(df.to_numpy(), cls=NumpyEncoder)
import pprint

# pprint.pprint(json_dump)
json_dump = json.dumps(df["rating"].to_numpy(), cls=NumpyEncoder)
# pprint.pprint(json_dump)

# Recommending movies when user has just watched Avatar (2009)
avatar_ratings = movie_matrix["Avatar (2009)"]
avatar_ratings = avatar_ratings.dropna()
print("\nRatings for 'Avatar (2009)':")
print(avatar_ratings.head())


avatar_user_rating = df.loc[(df["title"] == "Avatar (2009)") & (df["userId"] == 21)]
print(avatar_user_rating)

avatar_user_rating = movie_matrix["Avatar (2009)"]
avatar_user_rating.head()

print("&&&&&&&&&&&&&&&&&&&")
similar_to_avatar = movie_matrix.corrwith(avatar_user_rating, numeric_only=True)
# similar_to_avatar = movie_matrix.corrwith(avatar_user_rating)
print("&&&&&&&&&&&&&&&&&&&")
corr_avatar = pd.DataFrame(similar_to_avatar, columns=["correlation"])
corr_avatar.dropna(inplace=True)
corr_avatar = corr_avatar.join(df_ratings["number_of_ratings"])
print(corr_avatar.head(7))

# Read from JSON data source
# df_from_json = pd.read_json("main.json")
# json_str = df_from_json.to_json()

# Describe statistical properties on numeric data items
print("Describe statistical properties on numeric data items")
stats = movie_matrix.describe()
print(stats)


# Setting max-row display option to 20 rows.
# pd.set_option("max_rows", 20)

chart_1 = {
    "Name": ["Chetan", "yashas", "yuvraj"],
    "Age": [20, 25, 30],
    "Height": [155, 160, 175],
    "Weight": [55, 60, 75],
}
df1 = pd.DataFrame(chart_1)
chart_2 = {
    "Name": ["Pooja", "Sindu", "Renuka"],
    "Age": [18, 25, 20],
    "Height": [145, 155, 165],
    "Weight": [45, 55, 65],
}
df2 = pd.DataFrame(chart_2)
print(df1.corrwith(df2, numeric_only=True))
print(df1.corrwith(df2, method="pearson", numeric_only=True))
print(df1.corrwith(df2, method="kendall", numeric_only=True))
print(df1.corrwith(df2, method="spearman", numeric_only=True))


print("Movie reviews reloaded")
df_reviews = pd.read_csv("reviews.csv", na_values=missing_values)

print("Reload Movie titles")
df_movie_titles = pd.read_csv("movies.csv", na_values=missing_values)
print(df_movie_titles.shape)
df_movie_titles = extract_year(df_movie_titles)
df_movie_titles = genres_to_list(df_movie_titles)
print(df_movie_titles.shape)

df_movie_reviews = pd.merge(df_reviews, df_movie_titles, on="movieId")
df_movie_titles["number_of_ratings"] = df_movie_reviews.groupby("movieId")[
    "rating"
].count()
print("First movies", df_movie_titles.head())
print(df_movie_titles["title"])
print(df_movie_titles.loc[(df_movie_titles["title"] == "Avatar")])
print(
    df_movie_titles.loc[
        (df_movie_titles["title"] == "Avatar") & (df_movie_titles["year"] == "2009")
    ]
)
movies_with_years = df_movie_titles.loc[df_movie_titles["year"] != ""]
print(int(movies_with_years["year"].min()))
plt.figure(figsize=(18, 8), label="No of ratings vs year")
plt.scatter(movies_with_years["year"], movies_with_years["number_of_ratings"])
# plt.title("No of ratings vs year")
plt.ylabel("# of ratings")
plt.xlabel("Year")
plt.xticks(
    np.arange(
        int(movies_with_years["year"].min()),
        int(movies_with_years["year"].max()),
        5,
    )
)
plt.show()

# Correlation of the two numeric columns
print(movies_with_years[["year", "number_of_ratings"]].corr())
