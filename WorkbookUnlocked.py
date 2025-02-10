import os
import platform
import subprocess
from oyoms import WorkbookClient

class WorkbookUnlocked(WorkbookClient):
    """
    Extends WorkbookClient to add more methods for interacting with an Excel Workbook.
    """

    def insert_rows(self, sheet_name, range_address, shift="down"):
        """
        Insert rows into an Excel sheet using the Microsoft Graph API.

        Args:
            sheet_name: Name of the desired sheet.
            range_address: String with the Cell/Range address (A1 format).
            shift: Direction to shift existing rows. Options are "down" or "right". Default is "down".
        """
        # Create the sheet if it does not exist
        self.create_sheet(sheet_name)

        # Construct the request to insert rows
        url = f"/worksheets/{sheet_name}/range(address='{range_address}')/insert"
        request_body = {"shift": shift}

        # Send the request to the Graph API
        self.post(url, json=request_body)

    def export_pdf_local(self, sheet_name, new_name=None, open_file=False):
        """
        Export a specific worksheet as a PDF and save it locally.

        This method uses the Graph API conversion endpoint to convert the specified worksheet
        to PDF (via the ?format=pdf query parameter), writes the PDF content to a local file,
        and optionally opens the file with the default PDF viewer.

        Args:
            sheet_name: String specifying the worksheet name to export.
            new_name: Optional string for the new file name. If not provided, the workbook's name
                      is used with its extension replaced by '.pdf'.
            open_file: Optional Boolean. If True, opens the saved PDF file using the system's default viewer.
        
        Returns:
            The local file path of the saved PDF.
        """
        # Construct the Graph API endpoint for PDF conversion.
        export_endpoint = (
            f"/drives/{self.drive_id}/items/{self.item_id}/"
            f"workbook/worksheets/{sheet_name}/content?format=pdf"
        )

        # Request the PDF binary content.
        pdf_response = self.client.get(export_endpoint)
        if not pdf_response.ok:
            raise Exception(f"Failed to export PDF for sheet '{sheet_name}': {pdf_response.text}")
        pdf_content = pdf_response.content

        # Determine the filename.
        if new_name is None:
            # If the workbook has an attribute 'name', use it; otherwise use a default base name.
            if hasattr(self, 'name') and '.' in self.name:
                base = self.name.rsplit('.', 1)[0]
            else:
                base = "exported_sheet"
            new_name = base + '.pdf'
        else:
            if not new_name.lower().endswith('.pdf'):
                new_name += '.pdf'

        # Write the PDF content to a local file.
        local_file_path = os.path.join(os.getcwd(), new_name)
        with open(local_file_path, 'wb') as f:
            f.write(pdf_content)

        # Optionally open the file with the default viewer.
        if open_file:
            system = platform.system()
            try:
                if system == 'Windows':
                    os.startfile(local_file_path)
                elif system == 'Darwin':  # macOS
                    subprocess.call(['open', local_file_path])
                else:  # Linux and other OSes
                    subprocess.call(['xdg-open', local_file_path])
            except Exception as e:
                print(f"Failed to open file: {e}")

        return local_file_path