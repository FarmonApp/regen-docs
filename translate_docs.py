import argparse
import os
from pathlib import Path

from openai import AzureOpenAI

client = AzureOpenAI(
    # This is the default and can be omitted
    api_key="32a943563fed492397b60a760f12851d",
    azure_endpoint = "https://farmon-gpt.openai.azure.com/",
    api_version="2024-05-01-preview"
)

def main(language_code, language_name):
    # Define the path to the 'docs' directory
    docs_path = Path('docs')

    # Iterate over all Markdown files in 'docs' and subdirectories
    files = list(docs_path.glob(pattern='**/*.en.md'))
    for idx, md_file in enumerate(files):
        print(f"Processing file {idx + 1} of {len(files)}")
        # Skip files that are already in the target language
        if md_file.suffix == f".{language_code}.md":
            continue

        # Construct the translated file name
        translated_file = md_file.with_name(name=f"{md_file.stem[:-3]}.{language_code}{md_file.suffix}")

        # Skip if the translated file already exists
        if translated_file.exists():
            print(f"Skipping {md_file} as {translated_file} already exists.")
            continue

        # Read the original Markdown content
        with md_file.open('r', encoding='utf-8') as f:
            content = f.read()

        # Prepare messages for the Azure OpenAI ChatCompletion API
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that translates English markdown text into {language_name}, preserving the markdown formatting."
            },
            {
                "role": "user",
                "content": content
            }
        ]

        # Call the Azure OpenAI API to perform the translation
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5
            )

            # Extract the translated content
            translated_content = response.choices[0].message.content.strip()

            # Write the translated content to the new file
            with translated_file.open(mode='w', encoding='utf-8') as f:
                f.write(translated_content)

            print(f"Translated {md_file} to {translated_file}")

        except Exception as e:
            print(f"An error occurred while translating {md_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate Markdown files using Azure OpenAI.')
    parser.add_argument('--language-code', required=True, help='Target language code (e.g., "fr" for French)')
    parser.add_argument('--language-name', required=True, help='Target language name (e.g., "French")')

    args = parser.parse_args()

    main(language_code=args.language_code, language_name=args.language_name)