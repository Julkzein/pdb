# 🚀 QUICK START GUIDE

## Step 1: Start Backend

Open Terminal 1:
```bash
cd /Users/jules/Desktop/pdb/backend
source venv/bin/activate
python app_new.py
```

You should see:
```
============================================================
 🎯 Orchestration Graph Backend (Pure Python)
============================================================
 Library loaded: True
 Activities available: 10
 Graph initialized: True
------------------------------------------------------------
 Running at: http://127.0.0.1:5000
============================================================
```

**Leave this terminal running!**

## Step 2: Start Frontend

Open Terminal 2:
```bash
cd /Users/jules/Desktop/pdb/frontend
npm start
```

Browser will automatically open to `http://localhost:3000`

## Step 3: Test It!

1. You should see the header "🎯 Orchestration Graph Scheduler"
2. Connection status should show "Connected" (green)
3. On the right, you'll see 10 activities in green
4. Drag "Introduction" from the library to the timeline
5. It should appear as a colored block
6. Drag another activity after it
7. Click on the gap (space) between activities
8. Library will show recommendations with scores
9. Click "Add Recommended" to auto-fill

## ✅ Success Indicators

- Green "Connected" indicator in header
- 10 activities visible in library
- Activities can be dragged
- Timeline updates in real-time
- Gaps show when you click them
- Auto-add button works

## ❌ If Something's Wrong

**Backend won't start:**
- Make sure you're in the venv: `source venv/bin/activate`
- Check if Flask is installed: `pip list | grep Flask`
- Try: `pip install -r requirements.txt`

**Frontend won't start:**
- Make sure dependencies are installed: `npm install`
- Check if node_modules exists
- Try deleting node_modules and running `npm install` again

**Can't drag activities:**
- Check browser console (F12) for errors
- Make sure both backend and frontend are running
- Refresh the browser page

**No connection:**
- Verify backend is running on port 5000
- Check if port is blocked by firewall
- Try accessing http://127.0.0.1:5000/api/health in browser

## 🎯 Your First Lesson

1. Drag "Introduction" to the timeline → Appears in Class lane
2. Drag "PracticeMemory" after it → Appears in Indiv. lane
3. Click the gap between them → See recommendations
4. Drag "AdvancedOrganiser" (should score well) into the gap
5. Watch the hard gap indicator disappear!
6. Keep adding until "Goal reached: Yes ✓"

## 📖 Full Documentation

See `IMPLEMENTATION_GUIDE.md` for complete details.

---

**Enjoy your new Orchestration Graph Scheduler! 🎉**
