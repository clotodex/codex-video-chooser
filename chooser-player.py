#!/usr/bin/env python3

"""
This is an interactive tool to choose the next video to watch from a folder passed in as command line argument

First it shows a list of all mp4 files in the folder
Then the user can make a choice
And the video is played via mpv
"""

import argparse
import glob
import os
import re
import sys
import time
from collections import OrderedDict

from termcolor import colored


def split_by_channels(videos):
    """
    This function splits the list of video titles by channel.
    The title is in format 'channel name_rest of the filename.ext'
    """
    channel_dict = {}
    for video in videos:
        channel = os.path.basename(video).split("_")[0]
        if channel not in channel_dict:
            channel_dict[channel] = [video]
        else:
            channel_dict[channel].append(video)
    return channel_dict


def get_videos(path, extensions):
    """
    This function reads all video files from the folder passed as argument
    It returns all files with an extension of one of the following: mp4, mkv, avi, mov
    """
    videos = []
    for extension in extensions:
        videos += glob.glob(os.path.join(path, "*.{}".format(extension)))
    return videos


def play_video(filename):
    """
    Quotes the filename and plays the video via mpv
    After watching the video the user gets the option to delete the video
    """
    cmd = 'mpv "{}"'.format(filename)
    os.system(cmd)
    delete = input("Delete file? [y/N] ")
    if delete.lower() == "y":
        os.remove(filename)
    print()


def main():
    """
    Uses the functions 'get_videos', 'play_video', 'split_by_channels' to ask the user per channel what video she wants to watch next.
    The user will first choose a channel and then a video
    """
    parser = argparse.ArgumentParser(
        description="Interactive tool to choose the next video to watch from a channel"
    )
    parser.add_argument(
        "dir", help="The directory on your computer which contains the videos"
    )
    args = parser.parse_args()

    # prints a welcome message about the tool to the screen
    print(colored("Welcome to the interactive video chooser!", "cyan"))
    print(colored("----------------------------------------", "cyan"))
    print()

    extensions = ["mp4", "mkv", "avi", "mov"]

    videos = get_videos(args.dir, extensions)
    if len(videos) == 0:
        print("No videos found in folder {}".format(args.dir))
        sys.exit(0)

    videos_by_channel = split_by_channels(videos)

    # prints all channel names (and their amount of videos if more than 1) for the user to choose from via index starting at 1
    for index, channel in enumerate(videos_by_channel.keys()):
        videos_count = len(videos_by_channel[channel])
        if videos_count > 1:
            print(
                " ",
                colored(index + 1, "green"),
                channel,
                colored("({} videos)".format(videos_count), "cyan"),
            )
        else:
            print(" ", colored(index + 1, "green"), channel)

    # get the index of the channel the user wants to watch - if the user hit enter without typing anything, choose the first channel
    print()
    channel_index = input("Choose channel to watch next: ")
    if channel_index == "":
        print("No input - choosing first channel as default")
        channel_index = 0
    else:
        channel_index = int(channel_index) - 1
    if channel_index not in range(len(videos_by_channel.keys())):
        print("Channel index out of range")
        sys.exit(1)

    channel = list(videos_by_channel.keys())[channel_index]
    print()

    # prints all videos in the selected channel for the user to choose from via index starting at 1 - or plays the video directly if there is only one choice
    print(channel)
    videos = videos_by_channel[channel]
    if len(videos) == 1:
        play_video(videos[0])
        sys.exit(0)

    # sorts the videos by their timestamp - oldest first
    sorted_videos = sorted(videos, key=lambda x: os.path.getctime(x))

    for index, video in enumerate(sorted_videos):
        # format: index videoname-without-channelname (timestamp-human-readable-in-grey)
        video_name_without_channel = os.path.basename(video).replace(channel + "_", "")
        timestamp = os.path.getctime(video)
        timestamp_human_readable = time.strftime(
            "%a, %d %b %Y %H:%M:%S", time.localtime(timestamp)
        )
        print(
            " ",
            colored(index + 1, "green"),
            video_name_without_channel,
            colored("({})".format(timestamp_human_readable), "cyan"),
        )

    # adds an option for the user to watch all videos of the channel in order - sorted by their timestamp
    print(" ", colored(len(videos) + 1, "green"), "Play all videos")

    # get the index of the video the user wants to watch - if the user hit enter without typing anything, choose the first video
    video_index = input("Choose video to watch next: ")
    if video_index == "":
        print("No input - choosing first video as default")
        video_index = 0
    else:
        video_index = int(video_index) - 1
    if video_index not in range(len(sorted_videos) + 1):
        print("Video index out of range")
        sys.exit(1)

    if video_index == len(sorted_videos):
        # sorts the videos by their created date, oldest first, and plays them
        print()
        print("Playing all videos in order of creation date")
        for video in sorted_videos:
            play_video(video)
    else:
        play_video(videos[video_index])


if __name__ == "__main__":
    main()
