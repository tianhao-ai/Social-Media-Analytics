import json
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    start_time = time.time()
    
# Load tweet data from JSON file
with open('twitter-data-small.json') as f:
    tweets = json.load(f)

# Split the tweet data across processes
chunk_size = len(tweets) // size
start = rank * chunk_size
end = start + chunk_size 
my_tweets = tweets[start:end]

# Count the number of tweets made by each author
counts = {}
for tweet in my_tweets:
    author_id = tweet['data']['author_id']
    if author_id in counts:
        counts[author_id] += 1
    else:
        counts[author_id] = 1

# Combine the counts from all processes
all_counts = comm.gather(counts, root=0)

if rank == 0:
    # Merge the counts from all processes
    merged_counts = {}
    for counts in all_counts:
        for author_id, count in counts.items():
            if author_id in merged_counts:
                merged_counts[author_id] += count
            else:
                merged_counts[author_id] = count

    # Sort the authors by the number of tweets and present the top 10
    sorted_authors = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)
    top_authors = sorted_authors[:10]
    max_author_id_len = max(len(str(author_id)) for author_id, _ in top_authors)

    # Print the top 10 authors
    print(f"Rank\t{'Author Id':<{max_author_id_len}}\tNumber of Tweets Made")
    for i in range(len(top_authors)):
        author_id, num_tweets = top_authors[i]
        print(f"#{i+1}\t{author_id:<{max_author_id_len}}\t\t{num_tweets}")
    print(f"Elapsed time: {time.time() - start_time:.2f} seconds\n")