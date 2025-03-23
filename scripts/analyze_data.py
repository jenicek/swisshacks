#!/usr/bin/env python3
"""
Example data analysis script.
"""
import pandas as pd
import numpy as np


def main():
    print("SwissHacks Data Analysis")
    print("=======================")
    print("This is a placeholder for data analysis scripts.")
    
    # Example: Creating a sample dataframe
    data = {
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': np.random.randint(0, 100, 5)
    }
    df = pd.DataFrame(data)
    
    print("\nSample data:")
    print(df)
    
    print("\nSummary statistics:")
    print(df.describe())


if __name__ == "__main__":
    main()
