# 🧪 Testing the Real API Integration

## Quick Test Instructions

### 1. Verify Backend is Running
```powershell
# Check if port 8000 is in use
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# You should see the server running
```

### 2. Test via Python Script
```powershell
cd C:\Users\Poornima\Documents\GitHub\GeoSpark
python test_real_api.py
```

Expected output:
```
🔍 Testing GeoSpark Site Analysis API
📍 Location: Phoenix, Arizona (33.4484, -112.074)
📐 Area: 10 km²

⏳ Fetching real data from NASA POWER API...

✅ Analysis completed successfully!

============================================================
SOLAR POTENTIAL
============================================================
Annual Irradiance: 6.15 kWh/m²/day
Peak Sun Hours: 5.23 hours/day
Capacity Factor: 21.8%
Solar Score: 0.92/1.00

============================================================
WIND POTENTIAL
============================================================
Wind Speed (100m): 7.25 m/s
Wind Speed (10m): 5.39 m/s
Capacity Factor: 28.0%
Wind Score: 0.59/1.00

============================================================
✨ Real data fetched successfully from NASA POWER API!
============================================================
```

### 3. Test via Frontend

1. **Navigate to Site Analysis**
   - Open http://localhost:3000
   - Click "Site Analysis" in the navigation

2. **Search for a City**
   - Try these locations with known characteristics:

   **Phoenix, AZ (Excellent Solar):**
   - Search "Phoenix"
   - Expected: 6+ kWh/m²/day solar irradiance
   - Expected: 0.85+ solar score

   **Chicago, IL (Moderate):**
   - Search "Chicago"
   - Expected: 4-4.5 kWh/m²/day solar
   - Expected: 0.50-0.65 solar score

   **Seattle, WA (Low Solar):**
   - Search "Seattle"
   - Expected: 3-3.5 kWh/m²/day solar
   - Expected: 0.30-0.45 solar score

3. **Watch for Loading Message**
   - Button changes to "Fetching NASA satellite data..."
   - Toast shows: "Fetching real solar and wind data from NASA POWER API..."
   - Takes 3-7 seconds (real API call!)

4. **Verify Results**
   - Check that values change for different locations
   - Verify recommendations include actual metrics
   - Confirm risks mention data quality

## 🔍 What to Look For

### ✅ Success Indicators

1. **Variable Results**: Different cities show different values
2. **Realistic Values**: 
   - Solar: 2-7 kWh/m²/day (varies by location)
   - Wind: 4-12 m/s at 100m
3. **Loading Time**: 3-7 seconds (API is working)
4. **Detailed Recommendations**: Include specific numbers
5. **Data Quality Risk**: Always present in risk list

### ❌ Failure Indicators

1. **Same Results**: All cities show identical values → Fallback mode
2. **Instant Response**: <1 second → API not being called
3. **Generic Recommendations**: No specific numbers → Hardcoded mode
4. **Error Messages**: Check browser console and backend logs

## 🧪 Test Locations

### Solar Testing

| Location | Lat | Lon | Expected Solar | Score |
|----------|-----|-----|----------------|-------|
| Phoenix, AZ | 33.45 | -112.07 | 6.0-6.5 kWh/m²/day | 0.85-0.95 |
| Los Angeles, CA | 34.05 | -118.24 | 5.5-6.0 kWh/m²/day | 0.75-0.85 |
| Denver, CO | 39.74 | -104.99 | 5.0-5.5 kWh/m²/day | 0.70-0.80 |
| New York, NY | 40.71 | -74.01 | 4.0-4.5 kWh/m²/day | 0.50-0.60 |
| Seattle, WA | 47.61 | -122.33 | 3.0-3.5 kWh/m²/day | 0.30-0.45 |

### Wind Testing

| Location | Lat | Lon | Expected Wind (100m) | Score |
|----------|-----|-----|---------------------|-------|
| Amarillo, TX | 35.22 | -101.83 | 8-10 m/s | 0.70-0.85 |
| Boston, MA | 42.36 | -71.06 | 7-9 m/s | 0.60-0.75 |
| Chicago, IL | 41.88 | -87.63 | 7-9 m/s | 0.60-0.75 |
| Phoenix, AZ | 33.45 | -112.07 | 5-7 m/s | 0.40-0.60 |

## 🐛 Troubleshooting

### Problem: Analysis returns same values every time
**Cause**: API fallback mode is active
**Solution**:
1. Check backend logs for API errors
2. Verify internet connection
3. Try again later (NASA API may be down)

### Problem: "Analysis failed" error
**Check**:
```powershell
# Backend logs
cd C:\Users\Poornima\Documents\GitHub\GeoSpark
Get-Content -Path "app.log" -Tail 50
```

Common errors:
- `Connection refused` → Server not running
- `Timeout` → NASA API slow, increase timeout
- `401 Unauthorized` → Check authentication

### Problem: Very slow response (>20 seconds)
**Cause**: NASA POWER API can be slow sometimes
**Solutions**:
1. Increase timeout in site_selection.py (currently 15s)
2. Implement caching for repeated locations
3. Use alternative API (OpenMeteo)

### Problem: Frontend not updating
**Solutions**:
```powershell
# Clear browser cache
# Or hard refresh: Ctrl + Shift + R

# Restart frontend dev server
cd C:\Users\Poornima\Documents\GitHub\GeoSpark\frontend
npm run dev
```

## 📊 Comparing Old vs New

### Old System (Hardcoded)
```json
{
  "solar_potential": {
    "annual_irradiance_kwh_m2": 4.5,  // Always the same
    "solar_score": 0.8                 // Always the same
  }
}
```

### New System (Real Data)
```json
{
  "solar_potential": {
    "annual_irradiance_kwh_m2": 6.15,  // Changes by location
    "solar_score": 0.92                // Changes by location
  }
}
```

## 🔧 Advanced Testing

### Test API Fallback
Temporarily disable internet and verify:
1. Analysis still works
2. Uses latitude-based estimation
3. Returns reasonable default values

### Test Different Areas
Try various area sizes:
- Small: 1 km² → 10-20 MW capacity
- Medium: 10 km² → 100-200 MW capacity  
- Large: 100 km² → 500-1000 MW capacity

### Test Edge Cases
- **North Pole**: (90, 0) → Very low solar
- **Equator**: (0, 0) → High solar
- **Desert**: (30, 30) → Very high solar
- **Ocean**: (35, -50) → Good wind, low environmental score

## 📈 Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| NASA Solar API | 2-4s | Varies by server load |
| NASA Wind API | 2-4s | Varies by server load |
| Elevation API | 1-2s | Usually fast |
| Total Analysis | 3-7s | All APIs combined |

## ✅ Validation Checklist

Before marking complete, verify:

- [ ] Backend runs without errors
- [ ] Frontend loads properly
- [ ] City search works
- [ ] Analysis takes 3-7 seconds (real API)
- [ ] Results vary by location
- [ ] Solar scores realistic (0.3-0.95)
- [ ] Wind speeds realistic (4-12 m/s)
- [ ] Recommendations include metrics
- [ ] Risks include data quality note
- [ ] Loading messages appear
- [ ] Success toast shows "NASA data"
- [ ] No console errors
- [ ] Different cities = different results

## 🚀 Next Steps

Once testing is complete:
1. Document any API issues
2. Consider implementing caching
3. Monitor NASA API reliability
4. Prepare for production deployment
5. Add error tracking (Sentry)
6. Set up API monitoring

---

**Testing Complete!** 🎉

If all checks pass, your GeoSpark site analysis is now using real NASA satellite data for accurate renewable energy assessments.
