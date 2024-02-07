import streamlit as st
from stvis import pv_static
from main import get_followers_dfs, build_pyvis_graph

# set page to wide mode
def page_config():

    st.set_page_config(layout="wide", page_title="GitHub Network Visualizer", page_icon=":octocat:")

    # make logo and title on the upper right corner using html
    st.markdown(
        """
        <style>
            .logo {
                display: flex;
                align-items: center;
                justify-content: left;
            }
            .logo img {
                width: 100px;
                height: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div class="logo">
            <img src="https://github.com/iamaziz/st_ollama/assets/3298308/6af97d93-0e10-4586-aaa7-7d424925b5cc"/>
            <br><br>
            <h1 style="font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 44px;">GitHub Followers Network Graph</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("> _`Visualize the network of followers for a GitHub user and explore connections between users`_")
    st.markdown("---")


def graph_legend():
    # add legend for the graph
    st.markdown(
        """
        <details>
            <summary><b>Legend</b></summary>
            <ul>
                <li><b>Node</b>: User</li>
                <li><b>Directed Edge</b>: Follows</li>
            </ul>
            <ul>
            <li>
            <p>
            NOTE: node size is relative to the node's degree (number of connections) in the displayed network.<br>
            Hover over a node to see the user's GitHub profile link.<br>
            Click and drag to move the graph around.<br>
            Scroll to zoom in and out.<br>
            </p>
            </li>
            </ul>
        </details>
        """, unsafe_allow_html=True
    )


def visualize_graph(graph):

    graph_legend()
    pv_static(graph)


@st.cache_data(show_spinner=False)
def get_network(username, depth, github_token, max_followers):
    # if search_algo == "BFS":
    #     return get_followers_bfs(username, depth, github_token, max_followers)
    return get_followers_dfs(username, depth, github_token, max_followers)


def main():

    col1, col2 = st.columns(2)
    with col2:
        # GitHub API token input
        msg = "Optional as long as the daily rate limit of the default token isn't exceeded."
        msg += " Alternatively, you may generate a new token from your GitHub account settings > Developers Settings > Access Tokens. It's free and takes a few seconds."
        github_token = st.text_input("GitHub API Token (optional)", type="password", help=msg) or st.secrets["github_token"]["api_token"]
    with col1:
        # Username input to fetch network
        username = st.text_input("GitHub Username", placeholder="username")

    if not username or not github_token:
        return

    col1, col2, col3 = st.columns([1, 1, 2])
    # two sliders for depth and max followers
    with col1:
        max_followers = st.slider("Max Followers per User", min_value=2, max_value=30, value=5, help="The maximum number of followers to fetch for each user (API limit is 30)")
    # with col2:
        # search_algo = st.radio("Search Algorithm", ("BFS", "DFS"), index=0, help="BFS is faster but DFS may find more connections", horizontal=True)
    with col3:
        depth = st.slider("Depth", min_value=1, max_value=5, value=2)

    
    # Fetch network
    with st.spinner('Fetching network...'):
        network = get_network(username, depth, github_token, max_followers +1)

    # assert network
    assert len(network) > 0, (st.error("No network data found. Make sure the username and API token are correct"), st.stop())


    # Filter network by selected usernames from network
    nodes = set([x[0] for x in network] + [x[2] for x in network])
    selected_nodes = st.multiselect("Select users to visualize", nodes)
    if selected_nodes:
        network = [x for x in network if x[0] in selected_nodes or x[2] in selected_nodes]


    # Visualize network
    if network:
        with st.spinner('Visualizing network...'):
            graph = build_pyvis_graph(network)

            html = graph.generate_html("graph.html")
            # TODO: download the graph as html file
        
        visualize_graph(graph)
    else:
        st.write(network)
        st.error("No network data found.")


    # option to download the network as a csv file
    with st.expander("View Network Data"):
        st.json(network)

    # List all connections in the network as a markdown table
    st.subheader("Network Connections List")
    for i, (source, _, target) in enumerate(network):
        # add base url github.com/username to the source and target
        base_url = "https://github.com/"
        source = f"[{source}]({base_url + source})"
        target = f"[{target}]({base_url + target})"
        st.write(f"{i+1}. {source} `--follows-->` {target}")


if __name__ == "__main__":
    page_config()
    main()

