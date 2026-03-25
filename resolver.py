import pandas as pd
import argparse 
import os 

def main():
  # Setting up the Argument Parser 
  parser = argparse.ArgumentParser(description="Artist Social Media Resolver")
  parser.add_argument("input", help="Path to the input .xlsx file")
  parser.add_argument("output", help="Path to save the output .xlsx file")

  args = parser.parse_args()

  # Cheking if the input file exists
  if not os.path.exists(args.input):
    print(f"Error: The file {args.input} was not found.")
    return
  
  # Loading the Excel file using Pandas
  print(f"Loading {args.input}...")
  try:
    # Load the first 3 columns: Name, Spotify, Instagram 
    df = pd.read_excel(args.input)

    # Displaying the first 5 rows in the terminal to verify it works
    print("Successfully loaded. Here are the first 5 artists:")
    print(df.head())

    # For now, just save it back to the output path to test the 'write' logic
    df.to_excel(args.output, index=False)
    print(f"Test file created at: {args.output}")

  except Exception as e:
    print(f"An error occured: {e}")

if __name__ == "__main__":
  main()
