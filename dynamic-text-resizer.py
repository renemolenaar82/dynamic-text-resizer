import tkinter as tk
from tkinter import font as tkfont
import platform

class DynamicFontApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Font Size Text")
        
        # Make the window open maximized on both Windows and Linux
        self.maximize_window()
        
        # Set the background color of the root window
        self.root.configure(bg="black")
        
        # Create the text widget with black background and white text
        self.text_widget = tk.Text(
            root, 
            wrap="word", 
            padx=20, 
            pady=20,
            bg="black",    # Background color
            fg="white",    # Foreground (text) color
            insertbackground="white"  # Cursor color
        )
        self.text_widget.pack(fill="both", expand=True)
        
        # Set initial font
        self.font_family = "Arial"
        self.current_font_size = 72  # Start with a large font
        self.update_font()
        
        # Bind text changes to font size adjustment
        self.text_widget.bind("<<Modified>>", self.on_text_change)
        
        # Bind window resize events to adjust font
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Add cross-platform keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Flag to avoid recursive calls
        self.adjusting = False
        
        # Schedule window activation after the main loop starts
        self.root.after(100, self.activate_window)
    
    def maximize_window(self):
        """Maximize window using platform-specific methods"""
        # First update idle tasks to ensure window metrics are available
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set initial size (as fallback)
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Platform-specific maximization
        system = platform.system()
        if system == "Windows":
            self.root.state('zoomed')
        elif system == "Linux":
            self.root.attributes('-zoomed', True)
        else:  # macOS or other platforms
            # Try different methods
            try:
                self.root.state('zoomed')
            except:
                try:
                    self.root.attributes('-zoomed', True)
                except:
                    # Last resort - explicitly set window to use full screen dimensions
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    def activate_window(self):
        """Ensure window is active and has focus"""
        # Force window to be on top
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        
        # Give focus to the text widget
        self.text_widget.focus_set()
        
        # Place cursor in the text widget
        self.text_widget.mark_set(tk.INSERT, "1.0")
        
        # Ensure the window is drawn properly
        self.root.update_idletasks()
        
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts that work consistently across platforms"""
        # Bind Ctrl+A to select all text
        self.text_widget.bind("<Control-a>", self.select_all)
        
        # You can add more cross-platform shortcuts here if needed
        # For example:
        # self.text_widget.bind("<Control-c>", self.copy_text)
        # self.text_widget.bind("<Control-v>", self.paste_text)
        # self.text_widget.bind("<Control-x>", self.cut_text)
        
    def select_all(self, event=None):
        """Select all text in the text widget"""
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        self.text_widget.mark_set(tk.INSERT, tk.END)
        self.text_widget.see(tk.INSERT)
        return "break"  # Prevents default handling
        
    def update_font(self):
        custom_font = tkfont.Font(family=self.font_family, size=self.current_font_size)
        self.text_widget.configure(font=custom_font)
        
        # Ensure text is visible by scrolling to the beginning
        self.text_widget.see("1.0")
    
    def on_text_change(self, event=None):
        if self.text_widget.edit_modified() and not self.adjusting:
            self.adjust_font_size()
            self.text_widget.edit_modified(False)
    
    def on_window_resize(self, event=None):
        # Only respond to the root window resizing, not internal widget events
        if event and event.widget == self.root:
            # Small delay to let the window finish resizing
            self.root.after(100, self.adjust_font_size)
    
    def adjust_font_size(self):
        if self.adjusting:
            return
            
        self.adjusting = True
        
        text_content = self.text_widget.get("1.0", "end-1c")
        
        # Store cursor position
        cursor_pos = self.text_widget.index(tk.INSERT)
        
        if not text_content:
            self.current_font_size = 72
            self.update_font()
            self.adjusting = False
            return
        
        # Get window dimensions
        width = self.text_widget.winfo_width() - 40  # Account for padding
        height = self.text_widget.winfo_height() - 40
        
        if width <= 1 or height <= 1:  # Window not properly initialized yet
            self.root.after(100, self.adjust_font_size)
            self.adjusting = False
            return
        
        # Count explicit newlines in the text
        newline_count = text_content.count('\n')
        
        # Binary search to find the optimal font size
        min_size = 8  # Minimum readable size
        max_size = 200  # Start with a large size
        optimal_size = min_size
        
        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            test_font = tkfont.Font(family=self.font_family, size=mid_size)
            
            # Calculate text dimensions accounting for explicit newlines
            wrapped_lines = self.calculate_wrapped_lines(text_content, test_font, width)
            line_height = test_font.metrics("linespace")
            
            # The total number of lines is the number of wrapped lines
            total_height = len(wrapped_lines) * line_height
            
            if total_height <= height:
                optimal_size = mid_size
                min_size = mid_size + 1
            else:
                max_size = mid_size - 1
        
        # Apply a safety margin to ensure text fits
        self.current_font_size = max(8, optimal_size - 2)
        self.update_font()
        
        # Restore cursor position
        self.text_widget.mark_set(tk.INSERT, cursor_pos)
        
        # Ensure we can see where the cursor is
        self.text_widget.see(tk.INSERT)
        
        self.adjusting = False
    
    def calculate_wrapped_lines(self, text, font, width):
        """Calculate how many lines the text will take with wrapping, properly handling newlines."""
        if not text:
            return [""]
        
        # Split the text by explicit newlines first
        paragraphs = text.split('\n')
        all_lines = []
        
        for paragraph in paragraphs:
            # If paragraph is empty, it still counts as a line
            if not paragraph:
                all_lines.append("")
                continue
                
            words = paragraph.split()
            if not words:  # Handle paragraphs with only spaces
                all_lines.append("")
                continue
                
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if font.measure(test_line) <= width:
                    current_line = test_line
                else:
                    all_lines.append(current_line)
                    current_line = word
            
            if current_line or not words:  # Add the last line or an empty line
                all_lines.append(current_line)
        
        # Make sure we have at least one line
        if not all_lines:
            all_lines = [""]
            
        return all_lines

if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicFontApp(root)
    root.mainloop()