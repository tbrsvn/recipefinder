import os
import ujson as json
import subprocess

def clone_github_repo(repo_url, target_directory):
    # Check if the target directory exists, if not, create it
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # Clone the GitHub repository into the target directory
    print(f"Cloning {repo_url} into {target_directory}...")
    try:
        subprocess.run(['git', 'clone', repo_url, target_directory], check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return

def process_json_files(directory_path):
    result = {}

    for root, dirs, files in os.walk(directory_path):
        # Exclude the .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue

                # Use the "title" as the recipe name
                recipe_name = data.get("title", filename)
                result[recipe_name] = {
                    "directions": data["directions"],
                    "ingredients": data["ingredients"],
                    "language": data.get("language", ""),
                    "source": data.get("source", ""),
                    "title": data.get("title", ""),
                    "url": data.get("url", "")
                }

    return result

if __name__ == "__main__":
    # Clone the GitHub repository
    github_repo_url = "https://github.com/dpapathanasiou/recipes.git"
    target_directory = "recipes/index"
    clone_github_repo(github_repo_url, target_directory)

    # Process the JSON files in "recipes/index" directory
    input_directory = "recipes/index"
    output_file = "recipes.json"

    converted_data = process_json_files(input_directory)

    with open(output_file, 'w') as output:
        json.dump(converted_data, output, indent=4)

    print("Conversion complete. Result saved to", output_file)