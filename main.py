from functools import lru_cache
from collections import defaultdict

import requests
from pyvis.network import Network


@lru_cache(maxsize=128)
def get_followers_dfs(username, depth, token, max_followers=50):
    """
    Get the followers of a user up to a specified depth using GitHub token for authentication.
    :param username: GitHub username
    :param depth: Depth of network to explore
    :param token: GitHub personal access token for authentication
    :param max_followers: Maximum number of followers to fetch for each user
    :return: A set of tuples representing the network (USER_A, follows, USER_B)
    """
    network = set()
    to_explore = [(username, 0)]
    explored = set()

    headers = {'Authorization': f'token {token}'}

    while to_explore:
        current_user, current_depth = to_explore.pop(0)
        if current_user in explored or current_depth > depth:
            continue

        url = f"https://api.github.com/users/{current_user}/followers"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue

        followers = response.json()
        
        for follower in followers[:max_followers]:
            follower_login = follower['login']
            network.add((follower_login, "follows", current_user)) # network edge i.e. a triple
            to_explore.append((follower_login, current_depth + 1))

        explored.add(current_user)
        # time.sleep(1)  # to respect GitHub API rate limits

    return network


# a function to create a title for each node
def user_title(user):
    github_url = f"https://github.com/{user}"
    return f'<h4>{user}</h4><a href="{github_url}" target="_blank">{github_url}</a>'


# a function to calculate node size (adjust as needed)
def calculate_node_size(degree):
    base_size = 10  # Minimum size
    return base_size + degree * 1.5  # Scale size with degree


# a function to get colors based on degree
def get_colors(degree):
    if degree <= 5:
        return "blue", "yellow"
    elif degree <= 10:
        return "green", "orange"
    elif degree <= 15:
        return "orange", "red"
    else:
        return "red", "blue"


def build_pyvis_graph(network):

    net = Network(height="950px", width="1300px", bgcolor="#222222", font_color="white")

    # Calculate the degree for each node
    degrees = defaultdict(int)
    for source, _, target in network:
        degrees[source] += 1
        degrees[target] += 1

    # Add nodes with size based on degree and color based on degree
    for node in degrees:
        size = calculate_node_size(degrees[node])
        color = get_colors(degrees[node])[0]
        label = f"{node} ({degrees[node]})"
        title = f"degree: {degrees[node]}"
        net.add_node(node, label=label, title=title + user_title(node), hover=True, color=color, size=size)

    # Add edges
    for source, _, target in network:
        net.add_edge(source, target,
                    show_edge_weights=True,
                     arrows="to",
                     label="Follows",
                     font={"size": "7", "family": "courier", "align": "center", "strokeWidth": 0, "color": get_colors(degrees[source])[1]})

    # Set options (you can modify this part as needed)
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "dot",
        "size": 15,
        "font": {
          "size": 14
        }
      },
      "edges": {
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.35
        }
      },
        "physics": {
            "forceAtlas2Based": {
            "springLength": 100
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        }
    }
    """)

    return net


if __name__ == "__main__":
    # Example usage
    username = "iamaziz"
    depth = 2
    token = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
    network = get_followers_dfs(username, depth, token, max_followers=3)
    
    # Example usage
    # Assuming `network` is the set of tuples generated from the previous function
    graph = build_pyvis_graph(network)

