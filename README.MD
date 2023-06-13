# ChatGPT Query Module

This module provides functionality for interacting with OpenAI's ChatGPT model through a Tkinter-based GUI. It allows users to prime the model with a text document, send queries to the model, and view the conversation history and responses.

## Usage

To use this module, follow these steps:

1. Install the required dependencies:
    - Python (version 3.6 or higher)
    - `pip` package manager

2. Clone the repository or download the module file: `chatgpt_module.py`.

3. Install the necessary Python packages by running the following command:
    ```
    pip install -r requirements.txt
    ```

4. Run the module:
    ```
    python chatgpt_module.py
    ```

5. The GUI window will appear, allowing you to prime the model with a text document and send queries to the model.

## Dependencies

The module requires the following dependencies:

- Python (version 3.6 or higher)
- `openai` (version x.x.x)
- `tkinter` (included in Python standard library)
- `json` (included in Python standard library)
- `tkinter.filedialog` (included in Python standard library)
- `tkinter.messagebox` (included in Python standard library)

## Configuration

Before running the module, make sure to configure the following:

- Set your OpenAI API key in the module file:
    ```python
    openai.api_key = "YOUR_API_KEY"
    ```

- Adjust any other constants or settings in the module as required.

## Contributing

Contributions to this module are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This module is licensed under the [MIT License](LICENSE).

## Credits

This module was developed by Percy Rotteveel.