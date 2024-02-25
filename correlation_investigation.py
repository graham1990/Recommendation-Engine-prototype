import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as sci_stats

# Investigate correlation between item attributes


def generate_random_numbers(size=1000):
    return np.random.normal(0, 1, size)


def add_random_offset_to_array(loc, size=1000):
    return loc + np.random.normal(2, 1, size)


def correlation_ratio(categorical_feature, numeric_feature):
    """Correlation Ratio measures the correlation between a categorical column and a numeric column.
    It measures the variance of the mean of the numeric column across different categories of the categorical column.
    """
    cats, freqs = np.unique(categorical_feature, return_counts=True)
    numeric_mean = np.mean(numeric_feature)
    sig_y_bar = 0
    for i in range(len(cats)):
        category_mean = np.mean(numeric_feature[categorical_feature == cats[i]])
        sig_y_bar += np.square(category_mean - numeric_mean) * freqs[i]
    sig_y = np.sum(np.square(numeric_feature - numeric_mean))
    statistic = np.sqrt(sig_y_bar / sig_y)
    return statistic


def cramerv(a, b):
    """Cramer’s V correlation is a measure of the correlation between two categorical columns."""
    contingency = pd.crosstab(index=[a], columns=[b])
    chi2 = sci_stats.chi2_contingency(contingency)[0]
    n = np.sum(contingency.values)
    r, k = contingency.shape
    statistic = np.sqrt((chi2 / n) / min(r - 1, k - 1))
    return statistic


def cramerv_corrected(a, b):
    """Cramer’s V correlation is biased ."""
    contingency = pd.crosstab(index=[a], columns=[b])
    chi2 = sci_stats.chi2_contingency(contingency)[0]
    n = np.sum(contingency.values)
    r, k = contingency.shape
    phi2 = chi2 / n

    phi2_corrected = max(0, phi2 - (k - 1) * (r - 1) / (n - 1))
    r_corrected = r - (r - 1) ** 2 / (n - 1)
    k_corrected = k - (k - 1) ** 2 / (n - 1)

    statistic = np.sqrt(phi2_corrected / min(r_corrected - 1, k_corrected - 1))
    return statistic

if __name__ == "__main__":

    # Set seed
    np.random.seed(10)

    # Prepare data
    a = generate_random_numbers()
    b = add_random_offset_to_array(a)

    # Create scatter plot
    plt.figure(figsize=(8, 6), label="Spread of random data")
    for i, val in enumerate(a):
        plt.scatter(i, val)
    plt.show()

    # Pearson correlation assesses linear relationships, while Spearman correlation evaluates monotonic relationships.

    # Linear correlation between two sets of numeric data.
    print(f"Pearson Correlation = {sci_stats.pearsonr(a, b)}, {sci_stats.pearsonr(b, a)}")

    # The P-value is the probability that you would have found the current result if the correlation coefficient were in fact zero (null hypothesis). If this probability is lower than the conventional 5% (P<0.05) the correlation coefficient is called statistically significant.

    # Linear correlation between the ranks of two sets of numeric data.
    print(
        f"Spearman Correlation = {sci_stats.spearmanr(a, b)}, {sci_stats.spearmanr(b, a)}"
    )

    # Calculate correlations
    print(f"Correlation Ratio = {correlation_ratio(a, b)}, {correlation_ratio(b, a)}")

    # Calculate Cramer correlations
    print(f"Cramer's V Correlation = {cramerv(a, b)}, {cramerv(b, a)}")
    print(
        f"Cramer's V biased correction Correlation = {cramerv_corrected(a, b)}, {cramerv_corrected(b, a)}"
    )

    x = []
    y = []
    colours = [
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
    ]

    x.append("Pearson")
    value, _ = sci_stats.pearsonr(a, b)
    y.append(value)
    x.append("Spearman")
    value, _ = sci_stats.spearmanr(a, b)
    y.append(value)
    x.append("Correlation Ratio")
    y.append(correlation_ratio(a, b))
    x.append("Cramer's V")
    y.append(cramerv(a, b))
    # x.append("Cramer's V corrected")
    # y.append(cramerv_corrected(a, b))

    x.append("Pearson")
    value, _ = sci_stats.pearsonr(b, a)
    y.append(value)
    x.append("Spearman")
    value, _ = sci_stats.spearmanr(b, a)
    y.append(value)
    x.append("Correlation Ratio")
    y.append(correlation_ratio(b, a))
    x.append("Cramer's V")
    y.append(cramerv(b, a))

    plt.figure(figsize=(8, 6), label="Difference between data")
    plt.plot(list(range(0, 1000)), a)
    plt.plot(list(range(0, 1000)), b, '-.')
    plt.show()

    # Create scatter plot
    plt.figure(figsize=(8, 6), label="Correlation between x and y arrays")
    plt.scatter(x, y, c=colours)
    plt.show()

    print(a[0:5])
    print(b[0:5])
