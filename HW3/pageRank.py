def calculate_new_pagerank(current_ranks, links):
    new_ranks = {}

    # Calculate new PageRank for each page
    for page in current_ranks:
        # Find who links to this page
        incoming_links = [p for p, outgoing in links.items() if page in outgoing]

        # Sum up PageRank contributions
        rank_sum = 0
        for source_page in incoming_links:
            # Get number of outgoing links from source page
            num_outgoing = len(links[source_page])
            # Add contribution from this source page
            rank_sum += current_ranks[source_page] / num_outgoing

        new_ranks[page] = rank_sum

    return new_ranks

def print_ranks(ranks, iteration):
    print(f"\nPageRank values after iteration {iteration}:")
    print("-" * 35)
    print("Page  |  PageRank Value")
    print("-" * 35)
    for page, rank in ranks.items():
        print(f"  {page}   |     {rank:.3f}")
    print("-" * 35)

# Define the web structure
links = {
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/jet-lag': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/complementary-and-integrative'
    ],
    'https://www.cdc.gov/niosh/aviation/prevention/aircrew-jetlag.html': [
        'https://www.cdc.gov/niosh/aviation/prevention/aircrew-reproductive-health.html',
        'https://www.cdc.gov/niosh/aviation/prevention/'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/complementary-and-integrative': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/jet-lag',
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/deep-vein-thrombosis-and-pulmonary-embolism',
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/family/infants-and-children'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/mental-health': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/additional-considerations/substance-use',
        'https://www.cdc.gov/niosh/aviation/prevention/aircrew-jetlag.html'
    ],
    'https://www.cdc.gov/niosh/aviation/prevention/aircrew-reproductive-health.html': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/deep-vein-thrombosis-and-pulmonary-embolism'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/additional-considerations/substance-use': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/additional-considerations/substance-use'
    ],
    'https://www.cdc.gov/niosh/aviation/prevention/': [
        'https://www.cdc.gov/niosh/aviation/prevention/'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/pretravel-consultation': [
        'https://www.cdc.gov/niosh/aviation/prevention/'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/deep-vein-thrombosis-and-pulmonary-embolism': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/pretravel-consultation'
    ],
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/family/infants-and-children': [
        'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/mental-health'
    ]
}







# Initialize PageRank values (1/5 for each page)
pages =[
    'https://www.cdc.gov/niosh/aviation/prevention/',
    'https://www.cdc.gov/niosh/aviation/prevention/aircrew-jetlag.html',
    'https://www.cdc.gov/niosh/aviation/prevention/aircrew-reproductive-health.html',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/additional-considerations/substance-use',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/deep-vein-thrombosis-and-pulmonary-embolism',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/air-land-sea/jet-lag',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/family/infants-and-children',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/complementary-and-integrative',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/mental-health',
    'https://wwwnc.cdc.gov/travel/yellowbook/2024/preparing/pretravel-consultation'
]

current_ranks = {page: 1/5 for page in pages}

print("Web structure:")
for page, outlinks in links.items():
    print(f"Page {page} links to: {', '.join(outlinks)}")

# Print initial values
print("\nInitial PageRank Values:")
print_ranks(current_ranks, 0)

# First iteration
first_iteration = calculate_new_pagerank(current_ranks, links)
print_ranks(first_iteration, 1)

# Second iteration
second_iteration = calculate_new_pagerank(first_iteration, links)
print_ranks(second_iteration, 2)

# Find highest PageRank after second iteration
highest_page = max(second_iteration.items(), key=lambda x: x[1])
print(f"\nHighest PageRank after second iteration:")
print(f"Page {highest_page[0]} with PageRank value of {highest_page[1]:.3f}")