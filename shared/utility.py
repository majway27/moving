from datetime import datetime
import re
import os

def update_last_refreshed(index_html_path):
    """
    Updates the last-refreshed timestamp in index.html
    
    Args:
        index_html_path (str): Path to index.html file
    """
    try:
        # Read the current content of index.html
        with open(index_html_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Get current timestamp in desired format
        current_time = datetime.now().strftime('%B %d, %Y')
        
        # Replace content between span tags using regex
        updated_content = re.sub(
            r'<span id="last-refreshed">.*?</span>',
            f'<span id="last-refreshed">{current_time}</span>',
            content
        )
        
        # Write the updated content back to the file
        with open(index_html_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        print(f"Successfully updated last-refreshed timestamp to: {current_time}")
        
    except Exception as e:
        print(f"Error updating last-refreshed timestamp: {str(e)}")

if __name__ == "__main__":
    # When run directly, use relative path to index.html in parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(os.path.dirname(current_dir), 'index.html')
    update_last_refreshed(index_path) 