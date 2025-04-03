# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-execution,-papermill,-trusted,-slideshow
#     notebook_metadata_filter: -jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# Code generated with ChatGPT here: https://chatgpt.com/share/67ee9cf6-61e4-800a-a95c-372a73364432

# %%
import requests
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# --- CONFIGURATION ---
# Optionally, add your GitHub token here to increase your rate limit.
# For example: headers = {'Authorization': 'token YOUR_GITHUB_TOKEN'}
headers = {}

# GitHub search API endpoint for repositories
search_url = "https://api.github.com/search/repositories"
query = 'manubot in:readme'  # searches in the README
per_page = 100  # maximum per page
page = 1

# %%
# Store repositories
repos = []

# GitHub Search API returns up to 1000 results.
print("Querying GitHub API for repositories referencing manubot/rootstock...")
while True:
    params = {
        'q': query,
        'per_page': per_page,
        'page': page,
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        break

    data = response.json()
    items = data.get('items', [])
    if not items:
        break

    repos.extend(items)
    print(f"Fetched page {page} with {len(items)} repos.")
    
    # GitHub search API stops after 1000 results.
    if page * per_page >= min(data.get('total_count', 0), 1000):
        break

    page += 1
    time.sleep(1)  # be polite and avoid hitting rate limits

# %%
print(f"Total repositories found: {len(repos)}")

# %%
# --- PROCESS DATA ---
# Create a DataFrame with key info: name, created_at, language, and full URL.
data = []
for repo in repos:
    data.append({
        'name': repo['full_name'],
        'created_at': pd.to_datetime(repo['created_at']),
        'language': repo['language'] if repo['language'] else "Unknown",
        'url': repo['html_url']
    })

df = pd.DataFrame(data)

# %%
df.shape

# %%
df.head()

# %%
assert df["name"].is_unique
assert df["url"].is_unique

# %% [markdown]
# # PLOT USAGE OVER TIME

# %%
# --- ANALYZE USAGE OVER TIME ---
# Count new repositories per month.
df['month'] = df['created_at'].dt.to_period('M')
monthly_counts = df.groupby('month').size().reset_index(name='repo_count')
monthly_counts['month'] = monthly_counts['month'].dt.to_timestamp()

# %%
# Compute cumulative count over time
monthly_counts['cumulative'] = monthly_counts['repo_count'].cumsum()

# %%
sns.set(style="whitegrid")

# --- PLOT USAGE OVER TIME ---
plt.figure(figsize=(10, 5))
sns.lineplot(x='month', y='cumulative', data=monthly_counts, marker="o")
plt.title("Cumulative Number of Repositories Referencing manubot/rootstock")
plt.xlabel("Time")
plt.ylabel("Cumulative Count")
plt.xticks(rotation=45)
plt.tight_layout()

# %% [markdown]
# # PLOT USAGE OVER TIME (only HTML/TeX)

# %%
# --- ANALYZE USAGE OVER TIME ---
# Count new repositories per month.
monthly_counts = df[df["language"].isin(("TeX", "HTML"))].groupby('month').size().reset_index(name='repo_count')
monthly_counts['month'] = monthly_counts['month'].dt.to_timestamp()

# %%
# Compute cumulative count over time
monthly_counts['cumulative'] = monthly_counts['repo_count'].cumsum()

# %%
monthly_counts

# %%
sns.set(style="whitegrid")

# --- PLOT USAGE OVER TIME ---
plt.figure(figsize=(10, 5))
sns.lineplot(x='month', y='cumulative', data=monthly_counts, marker="o")
plt.title("Cumulative Number of Repositories Referencing manubot/rootstock")
plt.xlabel("Time")
plt.ylabel("Cumulative Count")
plt.xticks(rotation=45)
plt.tight_layout()

# %% [markdown]
# # ANALYZE LANGUAGE DISTRIBUTION

# %%
language_counts = df['language'].value_counts().reset_index()
language_counts.columns = ['language', 'count']

# %%
# Plot language distribution as a bar chart.
plt.figure(figsize=(10, 5))
sns.barplot(x='language', y='count', data=language_counts)
plt.title("Repositories by Primary Language")
plt.xlabel("Language")
plt.ylabel("Number of Repositories")
plt.xticks(rotation=45)
plt.tight_layout()

# %% [markdown]
# # ADDITIONAL STATISTICS

# %%
total_repos = len(df)
first_date = df['created_at'].min().strftime('%Y-%m-%d')
last_date = df['created_at'].max().strftime('%Y-%m-%d')
print(f"Total repositories found: {total_repos}")
print(f"First repository created on: {first_date}")
print(f"Most recent repository created on: {last_date}")
print("\nLanguage distribution:")
print(language_counts)

# %%
