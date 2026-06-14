# universal_harvester/agent/cdp_storage.py

def get_copilot_chat_ids(page):
    """
    Reads Copilot's IndexedDB to extract all chat IDs.
    This bypasses the sidebar entirely.
    """
    script = """
    async () => {
        const dbs = await indexedDB.databases();
        const dbInfo = dbs.find(db => db.name.includes("Copilot"));
        if (!dbInfo) return [];

        return new Promise((resolve, reject) => {
            const req = indexedDB.open(dbInfo.name);
            req.onerror = () => resolve([]);

            req.onsuccess = () => {
                const db = req.result;
                if (!db.objectStoreNames.contains("conversations")) {
                    resolve([]);
                    return;
                }
                const tx = db.transaction(["conversations"], "readonly");
                const store = tx.objectStore("conversations");

                const out = [];
                const cursorReq = store.openCursor();

                cursorReq.onsuccess = (e) => {
                    const cursor = e.target.result;
                    if (cursor) {
                        out.push(cursor.key); // chat_id
                        cursor.continue();
                    } else {
                        resolve(out);
                    }
                };
                cursorReq.onerror = () => resolve([]);
            };
        });
    }
    """
    return page.evaluate(script)