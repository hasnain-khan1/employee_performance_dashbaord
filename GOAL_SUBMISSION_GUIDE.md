# Goal Submission Guide

## Issue: "Submit for Approval" Not Working

### Root Cause
The goal submission was failing due to **Business Rule BR-013**: When submitting goals for approval, the **total weight across all employee goals must equal exactly 100%**.

### What Was Happening
- User creates a single goal with weight < 100% (e.g., 20%)
- User clicks "Submit for Approval"
- Backend validation rejects it because 20% ≠ 100%
- Error message wasn't being displayed properly in the frontend

### What We Fixed

#### 1. **Improved Error Handling**
Enhanced error message extraction in the frontend to properly display backend validation errors:
```javascript
// Now extracts and shows detailed validation errors including:
// - Field-specific errors (e.g., weight validation)
// - Non-field errors (e.g., max goals limit)
// - General API errors
```

#### 2. **Added Weight Total Indicator**
Added a real-time visual indicator that shows:
- Current total weight across all goals
- Weight of the current goal being created
- Combined total
- Color-coded status:
  - 🟢 **Green (Success)**: Total = 100% → Ready to submit
  - 🟡 **Yellow (Warning)**: Total < 100% → Save as draft, create more goals
  - 🔴 **Red (Error)**: Total > 100% → Reduce weight to stay within limit

### How to Successfully Submit Goals

#### Option 1: Create All Goals Before Submitting
1. **Create Goal 1** (Weight: 30%)
   - Click "Save as Draft"
2. **Create Goal 2** (Weight: 30%)
   - Click "Save as Draft"
3. **Create Goal 3** (Weight: 40%)
   - Click "Save as Draft"
4. **Submit each goal individually**:
   - Once total = 100%, click "Submit for Approval" on each goal
   - Or use the "Submit for Approval" button in the actions column

#### Option 2: Single Goal at 100%
1. **Create one comprehensive goal**
   - Set Weight: 100%
   - Click "Submit for Approval"

#### Option 3: Adjust Weights Later
1. **Create multiple draft goals**
2. **Adjust their weights** so they total 100%
3. **Submit for approval**

### Business Rules (Enforced by Backend)

- **BR-012**: Maximum **5 goals per employee** per review cycle
- **BR-013**: Total goal weights must equal **exactly 100%** when submitting
- **BR-014**: Goals cannot be **deleted once approved** (only edited with version history)
- **BR-015**: All goals must have **measurable metrics** (SMART validation)
- **BR-016**: Target dates must be **within the review cycle period**

### Error Messages You Might See

#### Weight Validation
```
Total weight must equal exactly 100% when submitting goals.
Current total: 60%.
Existing goals weight: 40%.
Adjust goal weights so they sum to 100%.
```
**Solution**: Create more goals or adjust weights to total 100%

#### Max Goals Limit
```
Maximum of 5 goals allowed per employee per cycle.
You currently have 5 goals.
Complete or cancel existing goals before creating new ones.
```
**Solution**: Cancel or complete existing goals before creating new ones

#### Date Validation
```
Target date cannot be after cycle end date (2025-12-31).
Goals must be achievable within the review cycle period.
```
**Solution**: Choose a target date within the review cycle

#### Metric Validation
```
Metric must contain quantifiable criteria.
Include specific numbers or measurable terms.
```
**Solution**: Add numbers or measurable terms like "25%", "10 projects", "2 hours"

### UI Features

#### Weight Total Indicator (New!)
Located below the Weight (%) field when creating a new goal:
- Shows real-time calculation of total weight
- Updates as you type in the weight field
- Provides clear guidance on whether you can submit or need to save as draft

#### Status Colors
- **Grey**: Draft
- **Orange**: Submitted (pending manager approval)
- **Blue**: Approved
- **Green**: Completed
- **Red**: Cancelled or Overdue

### Workflow Summary

```
1. Employee Creates Goals (Draft)
   ├─ Can create up to 5 goals
   ├─ Weights can be any value (1-100%)
   └─ Saved as "Draft" status

2. Employee Adjusts Weights
   ├─ Edit goals to adjust weights
   └─ Ensure total = 100%

3. Employee Submits for Approval
   ├─ Validation: Total weight = 100%
   ├─ Validation: All SMART criteria met
   └─ Status changes to "Submitted"

4. Manager Reviews and Approves
   ├─ Manager sees submitted goals
   ├─ Can approve or request changes
   └─ Status changes to "Approved"

5. Employee Tracks Progress
   ├─ Update progress percentage
   └─ Add goal updates
```

### Testing Steps

1. **Start fresh**: Clear any existing draft goals or set to cancelled
2. **Create first goal**: Weight 40%, Save as Draft
3. **Create second goal**: Weight 30%, Save as Draft
4. **Create third goal**: Weight 30%, Try to Submit for Approval
5. **Observe**: Should see success message and status changes to "Submitted"

### Support

If you encounter issues:
1. **Check browser console** for detailed error messages
2. **Verify weight total** equals 100% before submitting
3. **Check SMART criteria** are all filled in
4. **Ensure dates** are within the review cycle period
5. **Verify goal count** is not exceeding 5 goals

---

**Last Updated**: October 13, 2025
**Related Business Rules**: BR-012, BR-013, BR-014, BR-015, BR-016

