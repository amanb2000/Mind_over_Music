import sys
import os
import numpy as np
import pandas as pd
import reinforcementAgent as RA

def main():
    dqn = RA.DQN_Agent()
    test_data = [1, 2, 3, 4, 5]
    
    for i in range(100):
        print(dqn.run_data(test_data))
    

if __name__ == "__main__":
    main()

