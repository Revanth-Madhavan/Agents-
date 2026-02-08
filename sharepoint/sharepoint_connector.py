import os
from O365 import Account, FileSystemTokenBackend
from typing import List, Generator
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class SharePointFetcher:
    def __init__(self, client_id, client_secret, tenant_id=None):
        self.credentials = (client_id, client_secret)
        # Using FileSystemTokenBackend to store tokens locally
        self.token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
        self.account = Account(self.credentials, token_backend=self.token_backend, tenant_id=tenant_id)

    def authenticate(self):
        """Authenticates the user. Note: This may require manual intervention first run."""
        if not self.account.is_authenticated:
            # This prints a URL to visit and requires pasting the return URL.
            # In a real app, you'd handle the callback differently.
            # For CLI/Script usage:
            print("Authentication required.")
            self.account.authenticate(scopes=['basic', 'sharepoint_dl'])
            print("Authenticated successfully.")
        else:
            print("Already authenticated.")

    def get_site(self, site_name_or_url: str):
        """Finds and returns a SharePoint site object."""
        # This is a simplified search. O365 library site finding can be tricky.
        # Often easier to use the graph API directly if O365 lib is limited, 
        # but O365 lib has `sharepoint()` method.
        storage = self.account.storage()  # Access to OneDrive/SharePoint
        
        # If we want a specific site, we might need to search for it or use its ID.
        # For now, let's assume we want the root site or a search.
        # The O365 library's `storage` object usually maps to the user's default drive (OneDrive).
        # To access SharePoint sites, we need the `sharepoint` module.
        sharepoint = self.account.sharepoint()
        site = sharepoint.get_site(site_name_or_url) # Might need ID or URL
        return site

    def list_files(self, folder, supported_extensions=['.pdf', '.docx', '.txt', '.md']) -> Generator:
        """Recursively lists files in a folder."""
        for item in folder.get_items():
            if item.is_folder:
                yield from self.list_files(item, supported_extensions)
            elif item.is_file:
                 if any(item.name.lower().endswith(ext) for ext in supported_extensions):
                    yield item

    def download_files(self, site_name: str, library_name: str, target_dir: str):
        """Downloads files from a specific SharePoint library to a local directory."""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        sharepoint = self.account.sharepoint()
        # Note: Finding a site by name can be ambiguous. 
        # Using search is often better, or hardcoding the Site ID in a real app.
        # Here we attempt to find it.
        site = sharepoint.search_site(site_name)
        if not site:
            print(f"Site '{site_name}' not found.")
            return

        # Assuming the first result is the correct one if search returns a list, 
        # or it returns a single Site object.
        # O365 search_site returns a list usually.
        if isinstance(site, list):
            if not site:
                print(f"No site found matching '{site_name}'")
                return
            site = site[0] 
        
        print(f"Accessing Site: {site.name} ({site.web_url})")

        # Get the document library
        # This part can be tricky as libraries are 'drives' in Graph API.
        target_library = None
        drives = site.list_document_libraries()
        for drive in drives:
            if drive.name == library_name:
                target_library = drive
                break
        
        if not target_library:
            print(f"Library '{library_name}' not found in site '{site.name}'.")
            print("Available libraries:", [d.name for d in drives])
            return

        print(f"Found Library: {target_library.name}")
        root_folder = target_library.get_root_folder()

        for file_item in self.list_files(root_folder):
            local_path = os.path.join(target_dir, file_item.name)
            print(f"Downloading: {file_item.name} -> {local_path}")
            file_item.download(to_path=os.path.dirname(local_path))
            
if __name__ == "__main__":
    # Example usage
    CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET')
    
    if CLIENT_ID and CLIENT_SECRET:
        fetcher = SharePointFetcher(CLIENT_ID, CLIENT_SECRET)
        fetcher.authenticate()
        # Param 1: Site Name (keyword), Param 2: Library Name (usually 'Documents')
        fetcher.download_files("MyTargetSite", "Documents", "data/sharepoint_docs")
    else:
        print("Please set credentials in .env")
