#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from typing import Dict, List, Optional, Callable, Any
import weakref
from functools import lru_cache
import threading
from performance_monitor import monitor_performance, track_operation

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.scrolled import ScrolledFrame
    HAS_TTKBOOTSTRAP = True
except ImportError:
    import tkinter.ttk as ttk
    ttkb = ttk
    HAS_TTKBOOTSTRAP = False

class LazyCombobox(ttkb.Combobox if HAS_TTKBOOTSTRAP else tk.Listbox):
    """Optimized combobox that loads values lazily and caches results."""
    
    def __init__(self, parent, values_provider: Callable[[], List[str]], **kwargs):
        # Extract our custom parameters
        self.values_provider = values_provider
        self.loaded = False
        self._cached_values = None
        self._filter_text = ""
        
        # Initialize with empty values first
        if HAS_TTKBOOTSTRAP:
            super().__init__(parent, values=[], **kwargs)
            self.bind('<Button-1>', self._on_click)
            self.bind('<KeyRelease>', self._on_key_release)
        else:
            # Fallback for non-ttkbootstrap
            super().__init__(parent, **kwargs)
            self.bind('<Button-1>', self._on_click)
    
    @monitor_performance("LazyCombobox._load_values")
    def _load_values(self):
        """Load values from provider if not already loaded."""
        if not self.loaded:
            with track_operation("combobox_value_loading"):
                self._cached_values = self.values_provider()
                if HAS_TTKBOOTSTRAP:
                    self['values'] = self._cached_values
                else:
                    # For fallback listbox
                    self.delete(0, tk.END)
                    for value in self._cached_values:
                        self.insert(tk.END, value)
                self.loaded = True
    
    def _on_click(self, event=None):
        """Load values when user clicks on combobox."""
        if not self.loaded:
            # Load in background thread to avoid blocking UI
            threading.Thread(target=self._load_values, daemon=True).start()
    
    def _on_key_release(self, event=None):
        """Handle filtering as user types."""
        if not HAS_TTKBOOTSTRAP:
            return
            
        current_text = self.get().lower()
        if current_text != self._filter_text:
            self._filter_text = current_text
            self._filter_values()
    
    def _filter_values(self):
        """Filter values based on current text."""
        if not self.loaded:
            self._load_values()
        
        if self._cached_values and self._filter_text:
            filtered = [v for v in self._cached_values if self._filter_text in v.lower()]
            self['values'] = filtered[:50]  # Limit to 50 items for performance
        elif self._cached_values:
            self['values'] = self._cached_values[:50]  # Show first 50 items
    
    def refresh_values(self):
        """Force refresh of values from provider."""
        self.loaded = False
        self._cached_values = None
        self._load_values()

class VirtualScrollFrame(tk.Frame):
    """Virtual scrolling frame that only renders visible items for better performance."""
    
    def __init__(self, parent, item_height: int = 30, visible_items: int = 20, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.item_height = item_height
        self.visible_items = visible_items
        self.total_items = 0
        self.scroll_top = 0
        
        # Data
        self.items = []
        self.item_widgets = {}
        self.item_renderer = None
        
        # Create scrollbar
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self._on_scroll)
        self.scrollbar.pack(side="right", fill="y")
        
        # Create canvas for virtual scrolling
        self.canvas = tk.Canvas(self, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Frame inside canvas
        self.content_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Update scrollbar initially
        self._update_scrollbar()
    
    def set_item_renderer(self, renderer: Callable[[tk.Widget, Any, int], None]):
        """Set function to render items. Function should take (parent, item_data, index)."""
        self.item_renderer = renderer
    
    @monitor_performance("VirtualScrollFrame.set_items")
    def set_items(self, items: List[Any]):
        """Set the list of items to display."""
        self.items = items
        self.total_items = len(items)
        self._update_scrollbar()
        self._render_visible_items()
    
    def _update_scrollbar(self):
        """Update scrollbar configuration."""
        if self.total_items <= self.visible_items:
            # All items visible, hide scrollbar
            self.scrollbar.pack_forget()
            return
        
        self.scrollbar.pack(side="right", fill="y")
        
        # Calculate scroll region
        total_height = self.total_items * self.item_height
        visible_height = self.visible_items * self.item_height
        
        if total_height > 0:
            top_fraction = self.scroll_top / (self.total_items - self.visible_items)
            bottom_fraction = (self.scroll_top + self.visible_items) / self.total_items
            self.scrollbar.set(top_fraction, bottom_fraction)
    
    def _render_visible_items(self):
        """Render only the currently visible items."""
        if not self.item_renderer:
            return
        
        # Clear existing widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.item_widgets.clear()
        
        # Render visible items
        end_index = min(self.scroll_top + self.visible_items, self.total_items)
        
        for i in range(self.scroll_top, end_index):
            if i < len(self.items):
                item_frame = tk.Frame(self.content_frame, height=self.item_height)
                item_frame.pack(fill="x", pady=1)
                item_frame.pack_propagate(False)
                
                # Call renderer
                self.item_renderer(item_frame, self.items[i], i)
                self.item_widgets[i] = item_frame
        
        # Update canvas scroll region
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_scroll(self, *args):
        """Handle scrollbar movement."""
        action = args[0]
        
        if action == "scroll":
            delta = int(args[1])
            self.scroll_top = max(0, min(self.scroll_top + delta, 
                                        self.total_items - self.visible_items))
        elif action == "moveto":
            fraction = float(args[1])
            self.scroll_top = int(fraction * (self.total_items - self.visible_items))
        
        self._render_visible_items()
        self._update_scrollbar()
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        self.canvas.itemconfig(self.canvas.find_all()[0], width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if self.total_items <= self.visible_items:
            return
        
        delta = -1 if event.delta > 0 else 1
        self._on_scroll("scroll", delta)

class CachedDataProvider:
    """Provides cached data for UI components with automatic refresh."""
    
    def __init__(self, cache_duration: int = 300):  # 5 minutes default
        self.cache_duration = cache_duration
        self._cache = {}
        self._cache_times = {}
        self._callbacks = {}
    
    @lru_cache(maxsize=128)
    def get_staff_list(self) -> List[str]:
        """Get cached staff list."""
        return [
            "MY LUIS EDUARDO JEREZ",
            "CT PEDRO JOSE DIAZ BEDOYA",
            "CT JORGE ELIECER GOMEZ",
            "CT JAIME JUNIOR OSORIO",
            "CT NATALY CALIMAN",
            "CT DULZURA ANGELA MARIA RODRIGUEZ",
            "CT DIANA MARIA HUERTAS",
            "TE JOHANNA ROMERO",
            "TE HASBLEIDY GISETH ALMANSA HERRERA",
            "TE ASTRID VANESSA GUERRERO",
            "ST JHEIMY KATERINE HUERTAS GIL",
            "TS CARDONA ECHEVERRI BERNABE",
            "T1 BUITRAGO BEDOYA EVER JONNY",
            "T1 CAÑON PÁEZ NIDIA",
            "T1 MUÑOZ BOCANEGRA JORGE ELIECER",
            "T1 SALAMANCA LÓPEZ RAFAEL",
            "T1 ALVARADO YEPES ANGIE CATHERINE",
            "T1 SANDRA MILENA HERRERA CHAVEZ",
            "T1 MARLEN ALEXANDRA QUIÑONES PAEZ",
            "T1 CAROLINA CASTRO PUENTES",
            "T2 JULIAN SNAIDER OSORIO VANEGAS",
            "T2 SOCORRO MEJIA CARREÑO",
            "T2 RICHARD MCLAREN SANCHEZ PEINADO",
            "T2 JEISON JESUS ALTAMAR",
            "T2 HANNELY DIAZ MEDINA",
            "T2 DANIEL ORLANDO PINTO CORREAL",
            "T3 VALERIA HINOJOSA",
            "AT YORLENIS GISSEL CUESTA MORALES",
            "AT EDGAR ESNEIDER CRUZ SALCEDO",
            "SMSM DIEGO L MALPICA H"
        ]
    
    @lru_cache(maxsize=64)
    def get_camera_operators(self) -> List[str]:
        """Get cached camera operators list."""
        return [
            "CT DULZURA ANGELA MARIA RODRIGUEZ",
            "TS CARDONA ECHEVERRI BERNABE",
            "T1 CAÑON PÁEZ NIDIA",
            "T1 SALAMANCA LÓPEZ RAFAEL",
            "T1 ALVARADO YEPES ANGIE CATHERINE",
            "T2 JEISON JESUS ALTAMAR"
        ]
    
    @lru_cache(maxsize=32)
    def get_course_types(self) -> List[str]:
        """Get cached course types."""
        return ["Primera vez", "Recurrente"]
    
    @lru_cache(maxsize=32)
    def get_camera_profiles(self) -> List[str]:
        """Get cached camera profiles."""
        return ["IV-A", "Descompresión lenta"]
    
    def clear_cache(self):
        """Clear all cached data."""
        self.get_staff_list.cache_clear()
        self.get_camera_operators.cache_clear()
        self.get_course_types.cache_clear()
        self.get_camera_profiles.cache_clear()

class OptimizedFormBuilder:
    """Builder for optimized forms with lazy loading and performance optimizations."""
    
    def __init__(self, parent):
        self.parent = parent
        self.data_provider = CachedDataProvider()
        self.widgets = {}
        self.validators = {}
        
    @monitor_performance("OptimizedFormBuilder.create_field")
    def create_field(self, row: int, col: int, label: str, field_name: str, 
                    field_type: str = "entry", options: Optional[List[str]] = None,
                    width: int = 25, **kwargs) -> tk.Widget:
        """Create an optimized form field."""
        
        # Create label
        label_widget = ttkb.Label(self.parent, text=label)
        label_widget.grid(row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Create field based on type
        field_widget = None
        
        if field_type == "entry":
            field_widget = ttkb.Entry(self.parent, width=width, **kwargs)
        
        elif field_type == "combobox":
            if options:
                # Use regular combobox for small lists
                field_widget = ttkb.Combobox(self.parent, values=options, width=width, **kwargs)
            else:
                # Use lazy combobox for large lists
                provider = getattr(self.data_provider, f'get_{field_name}_list', 
                                 self.data_provider.get_staff_list)
                field_widget = LazyCombobox(self.parent, provider, width=width, **kwargs)
        
        elif field_type == "text":
            field_widget = tk.Text(self.parent, width=width, height=kwargs.get('height', 3))
        
        if field_widget:
            field_widget.grid(row=row, column=col+1, sticky="ew", padx=5, pady=2)
            self.widgets[field_name] = field_widget
        
        return field_widget
    
    def create_optimized_combobox(self, row: int, col: int, label: str, field_name: str,
                                data_source: str, **kwargs) -> LazyCombobox:
        """Create an optimized combobox with lazy loading."""
        
        # Map data sources to providers
        provider_map = {
            'staff': self.data_provider.get_staff_list,
            'camera_operators': self.data_provider.get_camera_operators,
            'courses': self.data_provider.get_course_types,
            'profiles': self.data_provider.get_camera_profiles
        }
        
        provider = provider_map.get(data_source, self.data_provider.get_staff_list)
        
        # Create label
        label_widget = ttkb.Label(self.parent, text=label)
        label_widget.grid(row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Create lazy combobox
        combobox = LazyCombobox(self.parent, provider, **kwargs)
        combobox.grid(row=row, column=col+1, sticky="ew", padx=5, pady=2)
        
        self.widgets[field_name] = combobox
        return combobox
    
    def add_validator(self, field_name: str, validator: Callable[[str], bool]):
        """Add validator for a field."""
        self.validators[field_name] = validator
        
        if field_name in self.widgets:
            widget = self.widgets[field_name]
            if hasattr(widget, 'bind'):
                widget.bind('<FocusOut>', lambda e: self._validate_field(field_name))
    
    def _validate_field(self, field_name: str) -> bool:
        """Validate a specific field."""
        if field_name not in self.validators or field_name not in self.widgets:
            return True
        
        widget = self.widgets[field_name]
        value = widget.get() if hasattr(widget, 'get') else ""
        
        is_valid = self.validators[field_name](value)
        
        # Update widget style based on validation
        if hasattr(widget, 'configure'):
            style = "success" if is_valid else "danger"
            widget.configure(bootstyle=style)
        
        return is_valid
    
    def validate_all(self) -> bool:
        """Validate all fields with validators."""
        all_valid = True
        for field_name in self.validators:
            if not self._validate_field(field_name):
                all_valid = False
        return all_valid
    
    def get_values(self) -> Dict[str, Any]:
        """Get all field values."""
        values = {}
        for field_name, widget in self.widgets.items():
            if hasattr(widget, 'get'):
                values[field_name] = widget.get()
        return values
    
    def set_values(self, values: Dict[str, Any]):
        """Set field values."""
        for field_name, value in values.items():
            if field_name in self.widgets:
                widget = self.widgets[field_name]
                if hasattr(widget, 'set'):
                    widget.set(value)
                elif hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))

# Global data provider instance
global_data_provider = CachedDataProvider()

# Convenience functions
def create_optimized_combobox(parent, values_provider: Callable[[], List[str]], **kwargs):
    """Create an optimized combobox with lazy loading."""
    return LazyCombobox(parent, values_provider, **kwargs)

def create_virtual_list(parent, items: List[Any], item_renderer: Callable, **kwargs):
    """Create a virtual scrolling list for large datasets."""
    virtual_frame = VirtualScrollFrame(parent, **kwargs)
    virtual_frame.set_item_renderer(item_renderer)
    virtual_frame.set_items(items)
    return virtual_frame