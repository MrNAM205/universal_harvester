import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DEFAULT_CHATS = "all_chats_verified.json"
DEFAULT_CLUSTERS = "clustered_chats.json"

class TopicBrowserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Universal Harvester – Topic Intelligence Browser")
        self.geometry("1100x700")

        self.chats = {}
        self.clusters = {}

        self._build_ui()
        self._auto_load()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # Left panel: Notebook (Tabs)
        left_panel = ttk.Frame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Topics (Semantic Clusters)
        self.tab_topics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_topics, text="Topics")
        
        self.topic_tree = ttk.Treeview(self.tab_topics, show="tree")
        self.topic_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.topic_tree.bind("<<TreeviewSelect>>", self.on_topic_select)

        # Tab 2: All Chats (Chronological/Raw)
        self.tab_chats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chats, text="All Chats")
        
        self.chat_listbox = tk.Listbox(self.tab_chats)
        self.chat_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_listbox.bind("<<ListboxSelect>>", self.on_chat_select)
        
        # Reload Button
        ttk.Button(left_panel, text="Refresh Data", command=self._auto_load).pack(fill="x", pady=2)

        # Right panel: Chat Viewer
        right_panel = ttk.Frame(self)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        self.chat_title_var = tk.StringVar(value="Select a chat from the left panel...")
        ttk.Label(right_panel, textvariable=self.chat_title_var, font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        self.text = tk.Text(right_panel, wrap="word", font=("Segoe UI", 10))
        self.text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

    def _auto_load(self):
        # 1. Load Raw Chats
        if os.path.exists(DEFAULT_CHATS):
            try:
                with open(DEFAULT_CHATS, "r", encoding="utf-8") as f:
                    chat_list = json.load(f)
                    self.chats = {c.get("id", f"unknown_{i}"): c for i, c in enumerate(chat_list)}
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {DEFAULT_CHATS}: {e}")
        
        self.chat_listbox.delete(0, tk.END)
        self.chat_listbox_keys = []
        for cid, c in self.chats.items():
            title = c.get("title") or cid
            self.chat_listbox.insert(tk.END, title)
            self.chat_listbox_keys.append(cid)

        # 2. Load Semantic Topic Clusters
        if os.path.exists(DEFAULT_CLUSTERS):
            try:
                with open(DEFAULT_CLUSTERS, "r", encoding="utf-8") as f:
                    self.clusters = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {DEFAULT_CLUSTERS}. Have you run cluster_topics.py yet?")
                self.clusters = {}

        self.topic_tree.delete(*self.topic_tree.get_children())
        if not self.clusters:
            self.topic_tree.insert("", "end", text="No clusters found. Run cluster_topics.py first.")
        else:
            for topic, meta_list in self.clusters.items():
                node = self.topic_tree.insert("", "end", text=f"📂 {topic} ({len(meta_list)} chats)", open=False)
                for meta in meta_list:
                    cid = meta.get("chat_id")
                    title = meta.get("title", cid)
                    # Store the Chat ID in the values tuple to retrieve it on click
                    self.topic_tree.insert(node, "end", text=f"📄 {title}", values=(cid,))

    def on_chat_select(self, event):
        idxs = self.chat_listbox.curselection()
        if not idxs:
            return
        cid = self.chat_listbox_keys[idxs[0]]
        self.display_chat(self.chats.get(cid))

    def on_topic_select(self, event):
        selected = self.topic_tree.selection()
        if not selected:
            return
        item = self.topic_tree.item(selected[0])
        values = item.get("values")
        if values:  # It's a leaf node (a specific chat)
            cid = values[0]
            self.display_chat(self.chats.get(cid))

    def display_chat(self, chat):
        if not chat: return
        self.chat_title_var.set(chat.get("title", "Unknown Chat"))
        self.text.delete("1.0", tk.END)
        for m in chat.get("messages", []):
            self.text.insert(tk.END, f"{m.get('role', 'unknown').upper()}:\n{m.get('text', '')}\n\n")
        self.text.mark_set("insert", "1.0")

if __name__ == "__main__":
    app = TopicBrowserApp()
    app.mainloop()