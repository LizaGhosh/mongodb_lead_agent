# How to View Logs in Vercel

This guide explains how to view and debug logs in Vercel to understand errors.

## ⚠️ Why You Might Not See Logs

If you're not seeing any logs in Vercel, here are common reasons:

1. **No Requests Made**: Logs only appear when functions are invoked. Make a request first!
2. **Looking in Wrong Place**: Logs are in the Functions tab, not the main deployment page
3. **Function Not Invoked**: Check if the function is actually being called
4. **Old Deployment**: The current deployment might not have logging code yet
5. **Log Level**: Some logs might be filtered out

## Quick Test: Verify Logging Works

1. **Test the logging endpoint**:
   ```
   https://your-app.vercel.app/api/test-logs
   ```
   This will print test messages that should appear in Vercel logs.

2. **Test health check**:
   ```
   https://your-app.vercel.app/api/health/db
   ```
   This will show MongoDB connection logs.

## Method 1: Vercel Dashboard (Recommended)

### Step 1: Access Your Project
1. Go to [vercel.com](https://vercel.com) and sign in
2. Navigate to your project: `mongodb_lead_agent`

### Step 2: View Function Logs
**IMPORTANT**: Logs are in the **Functions** section, not the main deployment page!

1. Click on your project
2. Go to the **"Deployments"** tab
3. Click on the **latest deployment** (or the one you want to check)
4. Scroll down to find **"Function Logs"** section
5. **OR** click on **"Functions"** tab in the left sidebar
6. Click on a function (e.g., `api/index.py`)
7. You'll see logs for that function

**Note**: If you don't see any logs:
- Make sure you've made a request to trigger the function
- Check that you're looking at the correct deployment
- Try the test endpoint: `/api/test-logs` to generate logs

### Step 3: Filter Logs
- Use the search bar to filter by:
  - `[VERCEL LOG]` - Request/response logs
  - `[MEETINGS]` - Meeting submission logs
  - `ERROR` - Error logs
  - `[ORCHESTRATOR]` - Agent workflow logs

## Method 2: Vercel CLI

### Install Vercel CLI
```bash
npm i -g vercel
```

### View Logs
```bash
# View logs for your project
vercel logs

# View logs for a specific deployment
vercel logs [deployment-url]

# Follow logs in real-time
vercel logs --follow

# Filter logs
vercel logs | grep "ERROR"
vercel logs | grep "[MEETINGS]"
```

## Method 3: Vercel Dashboard - Real-time Logs

1. Go to your project dashboard
2. Click on a specific deployment
3. Scroll down to **"Function Logs"** section
4. Logs update in real-time as requests come in

## Understanding Log Formats

### Request Logs
```
[VERCEL LOG] ========== REQUEST START ==========
[VERCEL LOG] Method: POST
[VERCEL LOG] Path: /api/meetings
[VERCEL LOG] Query: {}
[VERCEL LOG] Response Status: 200
[VERCEL LOG] ========== REQUEST END ==========
```

### Meeting Submission Logs
```
[MEETINGS] New meeting submission received
[MEETINGS] User ID: default
[MEETINGS] Has text: True, Length: 150
[MEETINGS] Has audio: False
[MEETINGS] Photo count: 2
[MEETINGS] ✅ Success! Meeting ID: abc123
```

### Error Logs
```
[VERCEL LOG] ========== ERROR OCCURRED ==========
[VERCEL LOG] Error Type: HTTPException
[VERCEL LOG] Error Message: Database connection failed
[VERCEL LOG] Traceback:
[full stack trace]
[VERCEL LOG] =====================================
```

## Common Log Patterns to Look For

### 404 Errors (Route Not Found)
```
[VERCEL LOG] Response Status: 404
```
**Solution**: Check `vercel.json` routing configuration

### 500 Errors (Server Error)
```
[MEETINGS] ❌ ERROR OCCURRED
[MEETINGS] Error Type: Exception
```
**Solution**: Check the full traceback in logs

### 503 Errors (MongoDB Connection)
```
[VERCEL LOG] Error Message: MongoDB connection error
```
**Solution**: Check MongoDB Atlas network access settings

### Network Errors
```
[VERCEL LOG] No response received
```
**Solution**: Check if serverless function is deployed correctly

## Tips for Debugging

1. **Use Print Statements**: `print()` statements show up clearly in Vercel logs
2. **Add Timestamps**: Logs automatically include timestamps
3. **Use Prefixes**: All logs use `[VERCEL LOG]` or `[MEETINGS]` prefixes for easy filtering
4. **Check Function Invocations**: In Vercel dashboard, check if functions are being invoked
5. **Check Environment Variables**: Ensure `MONGODB_URI` and other env vars are set

## Viewing Logs for Specific Errors

### If your friend gets a 404:
1. Check Vercel logs when they submit the form
2. Look for: `[VERCEL LOG] Response Status: 404`
3. Check if the route is being matched: `[VERCEL LOG] Path: /api/meetings`

### If there's a MongoDB error:
1. Look for: `[VERCEL LOG] Error Message: MongoDB`
2. Check: `/api/health/db` endpoint logs
3. Verify MongoDB Atlas network access

### If there's a timeout:
1. Check function execution time in logs
2. Look for: `[VERCEL LOG] Request took too long`
3. Consider increasing function timeout in Vercel settings

## Quick Debug Checklist

- [ ] Check Vercel dashboard → Functions → Logs
- [ ] Look for `[VERCEL LOG]` entries
- [ ] Check for `ERROR` or `❌` in logs
- [ ] Verify environment variables are set
- [ ] Test `/api/health` and `/api/health/db` endpoints
- [ ] Check MongoDB Atlas network access settings

## Troubleshooting: No Logs Showing

### Why You Might Not See Logs:

1. **No Function Invocations**
   - Logs only appear when functions are called
   - Check the "Invocations" count - if it's 0, no requests have been made
   - **Solution**: Make a request first (visit `/api/test-logs` or submit the form)

2. **Looking in Wrong Place**
   - Logs are NOT on the main project page
   - They're in: Deployments → [Select Deployment] → Function Logs
   - Or: Functions tab → [Select Function] → Logs
   - **Solution**: Navigate to the specific function's logs

3. **Old Deployment**
   - The current deployment might not have logging code
   - **Solution**: Push your changes and wait for new deployment

4. **Function Not Deployed**
   - Check if the function exists in Vercel
   - **Solution**: Verify `api/index.py` is in your project

5. **Logs Are Filtered**
   - Vercel might filter some logs
   - **Solution**: Use `print()` statements (they always show up)

### Quick Test Steps:

1. **Visit the test endpoint**:
   ```
   https://your-app.vercel.app/api/test-logs
   ```

2. **Immediately check Vercel logs**:
   - Go to Vercel Dashboard
   - Your Project → Deployments → Latest
   - Scroll to "Function Logs"
   - You should see `[TEST LOGS]` messages

3. **If still no logs**:
   - Check function invocations count (should be > 0)
   - Try Vercel CLI: `vercel logs --follow`
   - Make sure you're looking at the correct deployment

## Need Help?

If logs don't show up:
1. ✅ Make sure the deployment is active
2. ✅ Check that functions are being invoked (look for invocation count)
3. ✅ Try making a test request (`/api/test-logs`) and check logs immediately
4. ✅ Use `vercel logs --follow` for real-time monitoring
5. ✅ Verify you're looking at the correct function's logs
6. ✅ Push your latest changes with enhanced logging
