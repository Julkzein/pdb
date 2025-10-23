# ⚡ START HERE - 2 Minutes to Running App

## 🚀 Fastest Way to Start

### Open 2 Terminals

**Terminal 1 (Backend):**
```bash
cd /Users/jules/Desktop/pdb/backend
source venv/bin/activate
python app_new.py
```

**Terminal 2 (Frontend):**
```bash
cd /Users/jules/Desktop/pdb/frontend
npm start
```

**That's it!** Browser opens automatically to http://localhost:3000

---

## ✅ What You Should See

1. **Terminal 1 (Backend)**
   ```
   ✅ Loaded 10 activities
   ✅ Created new orchestration graph
   🎯 Orchestration Graph Backend (Pure Python)
   Library loaded: True
   Activities available: 10
   ```

2. **Terminal 2 (Frontend)**
   ```
   Compiled successfully!
   webpack compiled with 1 warning
   ```

3. **Browser**
   - Header: "🎯 Orchestration Graph Scheduler"
   - Status: "Connected" (green)
   - Right side: 10 green activity cards
   - Center: Empty timeline

---

## 🎯 First Test (30 seconds)

1. **Drag** "Introduction" from right panel to timeline
2. **See** it appear as a colored block
3. **Drag** "PracticeMemory" after it
4. **Click** the gap between them
5. **See** recommendations appear (scored activities)
6. **Click** "Add Recommended" button
7. **See** new activity added automatically

**Success!** ✨ Your app is working!

---

## 📖 More Info

- **FINAL_SUMMARY.md** - Complete guide with troubleshooting
- **START_APP.md** - Detailed startup instructions
- **IMPLEMENTATION_GUIDE.md** - Full technical documentation

---

## 🐛 Problems?

**Backend won't start?**
```bash
cd /Users/jules/Desktop/pdb/backend
pip install Flask Flask-CORS
```

**Frontend won't start?**
```bash
cd /Users/jules/Desktop/pdb/frontend
npm install
```

**Still stuck?**
- Check FINAL_SUMMARY.md for detailed troubleshooting
- Open browser console (F12) for frontend errors
- Check backend terminal for Python errors

---

## 🎉 You're Ready!

Just run those 2 terminal commands above and start building lessons!

**Next:** Try the "First Test" above to verify everything works.
