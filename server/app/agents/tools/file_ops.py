import os
from datetime import datetime

class FileOps:

    def __init__(self):
        # get all available tools
        self.tools = self.get_tools()
        
    def save_html_to_file(self, content: str, file_path: str):
        try:
            # Normalize path
            file_path = os.path.normpath(file_path)
            
            # Ensure directory exists
            self.ensure_directory_exists(file_path)
            
            # Write file
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(content)
                
        except Exception as e:
            raise Exception(f"Error saving HTML to file: {str(e)}")

    def ensure_directory_exists(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def date_time_now(self) -> str:
        return str(int(datetime.now().timestamp()))
    
    def get_tools(self):
        available_tools = [self.save_html_to_file, self.ensure_directory_exists, self.date_time_now]
        return available_tools
        