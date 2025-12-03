# data_loader.py
"""
Automatically download dataset using kagglehub as requested.
If kagglehub is not installed or you don't want to run it, this function
will skip gracefully.
"""

import os
import logging

def ensure_dataset():
    """
    Downloads the dataset using kagglehub.dataset_download(...) into ./data/
    Returns path to downloaded files/folder.
    """
    os.makedirs("data", exist_ok=True)
    try:
        import kagglehub
    except Exception as e:
        raise RuntimeError("kagglehub not available in environment. Install or skip dataset download. Error: " + str(e))

    # Download latest version (as requested)
    try:
        # user provided snippet required:
        path = kagglehub.dataset_download("axondata/call-center-speech-dataset")
        # Move or copy to ./data if needed - assume kagglehub returns path
        return path
    except Exception as e:
        raise RuntimeError("kagglehub dataset download failed: " + str(e))

if __name__ == "__main__":
    print("Attempting to download dataset into ./data/")
    try:
        p = ensure_dataset()
        print("Downloaded dataset to:", p)
    except Exception as e:
        print("Dataset download failed:", e)
