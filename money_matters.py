import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBWl3XByOdS-z5Xcva5W0DZirXihdyDjyU"

# YouTube API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("Fresh Viral Topic Tool")

# Input Fields
days = st.number_input(
    "Enter Days to Search (1-30):",
    min_value=1,
    max_value=30,
    value=5
)

# List of broader keywords
keywords = [
"Financial Freedom", "Financial Literacy", "Financial Stability", "Financial Crisis",
"Financial Traps", "Financial Mistakes", "Financial Habits", "Financial Reality",
"Financial Strategy", "Financial System", "Financial Education", "Financial Planning",
"Financial Independence", "Financial Reset", "Money Habits", "Money Rules",
"Money Mistakes", "Money Stats", "Money Lessons", "Money Myths",
"Money Management", "Money Mindset", "Wealth Habits", "Wealth Building",
"Wealth Creation", "Wealth Inequality", "Wealth Transfer", "Net Worth",
"Passive Income", "Compound Interest", "Credit Score Loophole", "Emergency Fund",
"Retirement Savings", "Debt Payoff", "Budget System", "Paycheck Routine"
]
# Fetch Data Button
if st.button("Fetch Data"):

    try:
        # Calculate date range
        start_date = (
            datetime.utcnow() - timedelta(days=int(days))
        ).isoformat("T") + "Z"

        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:

            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(
                YOUTUBE_SEARCH_URL,
                params=search_params
            )

            data = response.json()

            # Check if videos exist
            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]

            video_ids = [
                video["id"]["videoId"]
                for video in videos
                if "id" in video and "videoId" in video["id"]
            ]

            channel_ids = [
                video["snippet"]["channelId"]
                for video in videos
                if "snippet" in video and "channelId" in video["snippet"]
            ]

            if not video_ids or not channel_ids:
                st.warning(
                    f"Skipping keyword: {keyword} due to missing video/channel data."
                )
                continue

            # Fetch video statistics
            video_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY
            }

            video_response = requests.get(
                YOUTUBE_VIDEO_URL,
                params=video_params
            )

            stats_data = video_response.json()

            if "items" not in stats_data:
                st.warning(f"Failed to fetch video stats for {keyword}")
                continue

            stats = stats_data["items"]

            # Fetch channel statistics
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }

            channel_response = requests.get(
                YOUTUBE_CHANNEL_URL,
                params=channel_params
            )

            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(
                    f"Failed to fetch channel statistics for keyword: {keyword}"
                )
                continue

            channels = channel_data["items"]

            # Collect results
            for video, stat, channel in zip(videos, stats, channels):

                title = video["snippet"].get("title", "N/A")

                description = video["snippet"].get(
                    "description",
                    ""
                )[:200]

                video_url = (
                    f"https://www.youtube.com/watch?v="
                    f"{video['id']['videoId']}"
                )

                views = int(
                    stat["statistics"].get("viewCount", 0)
                )

                subs = int(
                    channel["statistics"].get(
                        "subscriberCount",
                        0
                    )
                )

                # Only include small channels
                if subs < 10000:

                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:

            st.success(
                f"Found {len(all_results)} results across all keywords!"
            )

            for result in all_results:

                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )

                st.write("---")

        else:
            st.warning(
                "No results found for channels with fewer than 3,000 subscribers."
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
